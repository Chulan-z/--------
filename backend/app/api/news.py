from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session, joinedload

from app.api.deps import client_ip, get_current_admin
from app.db.session import get_db
from app.models.article import NewsArticle
from app.models.category import Category
from app.models.source import NewsSource
from app.models.user import User
from app.schemas.common import Message
from app.schemas.news import ArticleCreate, ArticleOut, ArticleUpdate, CategoryOut, SourceCreate, SourceOut, SourceUpdate
from app.services.audit import write_log
from app.services.news_aggregator import fetch_all_sources

router = APIRouter(tags=["news"])


@router.get("/articles", response_model=list[ArticleOut])
def list_articles(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None, max_length=100),
    category: str | None = Query(default=None, max_length=100),
    source_id: int | None = None,
    limit: int = Query(default=30, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[NewsArticle]:
    query = db.query(NewsArticle).options(joinedload(NewsArticle.source), joinedload(NewsArticle.category_ref))
    if q:
        query = query.filter(NewsArticle.title.ilike(f"%{q}%"))
    if category:
        query = query.filter(NewsArticle.category == category)
    if source_id:
        query = query.filter(NewsArticle.source_id == source_id)
    return (
        query.order_by(
            NewsArticle.is_featured.desc(),
            NewsArticle.published_at.desc().nullslast(),
            NewsArticle.fetched_at.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)) -> list[Category]:
    return db.query(Category).order_by(Category.name).all()


@router.get("/sources", response_model=list[SourceOut])
def list_sources(db: Session = Depends(get_db)) -> list[NewsSource]:
    return db.query(NewsSource).order_by(NewsSource.name).all()


def _get_or_create_category(db: Session, name: str) -> Category:
    category_name = name.strip()[:100] or "Редакция"
    category = db.query(Category).filter(Category.name == category_name).one_or_none()
    if category is None:
        category = Category(name=category_name)
        db.add(category)
        db.flush()
    return category


def _manual_source(db: Session) -> NewsSource:
    source = db.query(NewsSource).filter(NewsSource.url == "https://local.news/manual").one_or_none()
    if source is None:
        source = NewsSource(name="Редакция агрегатора", url="https://local.news/manual", type="api", is_active=False)
        db.add(source)
        db.flush()
    return source


@router.post("/admin/articles", response_model=ArticleOut, status_code=201)
def create_article(
    payload: ArticleCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> NewsArticle:
    source = db.get(NewsSource, payload.source_id) if payload.source_id else _manual_source(db)
    if source is None:
        raise HTTPException(status_code=404, detail="Источник не найден")
    category = _get_or_create_category(db, payload.category)
    article = NewsArticle(
        source_id=source.id,
        category_id=category.id,
        title=payload.title,
        content=payload.content,
        url=str(payload.url) if payload.url else f"https://local.news/manual/{uuid4()}",
        image_url=str(payload.image_url) if payload.image_url else None,
        published_at=payload.published_at or datetime.now(timezone.utc),
        fetched_at=datetime.now(timezone.utc),
        category=category.name,
        is_featured=payload.is_featured,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    write_log(
        db,
        action="article_create",
        entity="news_articles",
        message=f"Администратор добавил новость: {article.title}",
        user_id=admin.id,
        ip_address=client_ip(request),
    )
    return article


@router.patch("/admin/articles/{article_id}", response_model=ArticleOut)
def update_article(
    article_id: int,
    payload: ArticleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> NewsArticle:
    article = db.get(NewsArticle, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    data = payload.model_dump(exclude_unset=True)
    if "source_id" in data and data["source_id"] is not None and db.get(NewsSource, data["source_id"]) is None:
        raise HTTPException(status_code=404, detail="Источник не найден")
    if "category" in data and data["category"] is not None:
        category = _get_or_create_category(db, data.pop("category"))
        article.category_id = category.id
        article.category = category.name
    for key, value in data.items():
        if key in {"url", "image_url"} and value is not None:
            value = str(value)
        setattr(article, key, value)
    db.commit()
    db.refresh(article)
    write_log(
        db,
        action="article_update",
        entity="news_articles",
        message=f"Администратор обновил новость: {article.title}",
        user_id=admin.id,
        ip_address=client_ip(request),
    )
    return article


@router.delete("/admin/articles/{article_id}", response_model=Message)
def delete_article(article_id: int, request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)) -> Message:
    article = db.get(NewsArticle, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    title = article.title
    db.delete(article)
    db.commit()
    write_log(
        db,
        action="article_delete",
        entity="news_articles",
        message=f"Администратор удалил новость: {title}",
        user_id=admin.id,
        ip_address=client_ip(request),
    )
    return Message(message="Новость удалена")


@router.post("/admin/sources", response_model=SourceOut, status_code=201)
def create_source(payload: SourceCreate, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> NewsSource:
    source = NewsSource(name=payload.name, url=str(payload.url), type=payload.type, is_active=payload.is_active)
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.patch("/admin/sources/{source_id}", response_model=SourceOut)
def update_source(source_id: int, payload: SourceUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> NewsSource:
    source = db.get(NewsSource, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Источник не найден")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(source, key, str(value) if key == "url" else value)
    db.commit()
    db.refresh(source)
    return source


@router.delete("/admin/sources/{source_id}", response_model=Message)
def delete_source(source_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> Message:
    source = db.get(NewsSource, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Источник не найден")
    db.delete(source)
    db.commit()
    return Message(message="Источник удален")


@router.post("/admin/aggregate")
def aggregate(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> dict[str, int]:
    return fetch_all_sources(db)
