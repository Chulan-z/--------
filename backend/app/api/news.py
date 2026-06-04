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

CATEGORY_ORDER = [
    "\u0412\u0430\u0436\u043d\u0430\u044f",
    "\u041c\u0438\u0440",
    "\u041f\u0440\u043e\u0438\u0441\u0448\u0435\u0441\u0442\u0432\u0438\u044f",
    "\u0413\u043e\u0440\u043e\u0434",
    "\u041e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u0435",
    "\u0422\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0438",
    "\u0421\u043f\u043e\u0440\u0442",
    "\u041a\u0443\u043b\u044c\u0442\u0443\u0440\u0430",
]
MANUAL_SOURCE_NAME = "\u0420\u0435\u0434\u0430\u043a\u0446\u0438\u044f \u0430\u0433\u0440\u0435\u0433\u0430\u0442\u043e\u0440\u0430"
IMPORTANT_CATEGORY = "\u0412\u0430\u0436\u043d\u0430\u044f"


@router.get("/articles", response_model=list[ArticleOut])
def list_articles(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None, max_length=100),
    category: str | None = Query(default=None, max_length=100),
    source_id: int | None = None,
    limit: int = Query(default=100, le=200),
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
    categories = db.query(Category).all()
    return sorted(categories, key=lambda category: CATEGORY_ORDER.index(category.name) if category.name in CATEGORY_ORDER else 100)


@router.get("/sources", response_model=list[SourceOut])
def list_sources(db: Session = Depends(get_db)) -> list[NewsSource]:
    return db.query(NewsSource).order_by(NewsSource.name).all()


def _get_or_create_category(db: Session, name: str) -> Category:
    category_name = name.strip()[:100] or IMPORTANT_CATEGORY
    category = db.query(Category).filter(Category.name == category_name).one_or_none()
    if category is None:
        category = Category(name=category_name)
        db.add(category)
        db.flush()
    return category


def _manual_source(db: Session) -> NewsSource:
    source = db.query(NewsSource).filter(NewsSource.url == "https://local.news/manual").one_or_none()
    if source is None:
        source = NewsSource(name=MANUAL_SOURCE_NAME, url="https://local.news/manual", type="api", is_active=False)
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
        raise HTTPException(status_code=404, detail="Source not found")
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
        is_featured=category.name == IMPORTANT_CATEGORY,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    write_log(
        db,
        action="article_create",
        entity="news_articles",
        message=f"Admin created article: {article.title}",
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
        raise HTTPException(status_code=404, detail="Article not found")
    data = payload.model_dump(exclude_unset=True)
    if "source_id" in data and data["source_id"] is not None and db.get(NewsSource, data["source_id"]) is None:
        raise HTTPException(status_code=404, detail="Source not found")
    if "category" in data and data["category"] is not None:
        category = _get_or_create_category(db, data.pop("category"))
        article.category_id = category.id
        article.category = category.name
        article.is_featured = category.name == IMPORTANT_CATEGORY
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
        message=f"Admin updated article: {article.title}",
        user_id=admin.id,
        ip_address=client_ip(request),
    )
    return article


@router.delete("/admin/articles/{article_id}", response_model=Message)
def delete_article(article_id: int, request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)) -> Message:
    article = db.get(NewsArticle, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    title = article.title
    db.delete(article)
    db.commit()
    write_log(
        db,
        action="article_delete",
        entity="news_articles",
        message=f"Admin deleted article: {title}",
        user_id=admin.id,
        ip_address=client_ip(request),
    )
    return Message(message="Article deleted")


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
        raise HTTPException(status_code=404, detail="Source not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(source, key, str(value) if key == "url" else value)
    db.commit()
    db.refresh(source)
    return source


@router.delete("/admin/sources/{source_id}", response_model=Message)
def delete_source(source_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> Message:
    source = db.get(NewsSource, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    db.delete(source)
    db.commit()
    return Message(message="Source deleted")


@router.post("/admin/aggregate")
def aggregate(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> dict[str, int]:
    return fetch_all_sources(db)
