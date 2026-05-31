from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.article import NewsArticle
from app.models.category import Category
from app.models.source import NewsSource
from app.models.user import User
from app.schemas.common import Message
from app.schemas.news import ArticleOut, CategoryOut, SourceCreate, SourceOut, SourceUpdate
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
    return query.order_by(NewsArticle.published_at.desc().nullslast(), NewsArticle.fetched_at.desc()).offset(offset).limit(limit).all()


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)) -> list[Category]:
    return db.query(Category).order_by(Category.name).all()


@router.get("/sources", response_model=list[SourceOut])
def list_sources(db: Session = Depends(get_db)) -> list[NewsSource]:
    return db.query(NewsSource).order_by(NewsSource.name).all()


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
        from fastapi import HTTPException

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
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Источник не найден")
    db.delete(source)
    db.commit()
    return Message(message="Источник удален")


@router.post("/admin/aggregate")
def aggregate(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> dict[str, int]:
    return fetch_all_sources(db)
