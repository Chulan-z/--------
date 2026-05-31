from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx
from sqlalchemy.orm import Session

from app.models.article import NewsArticle
from app.models.category import Category
from app.models.source import NewsSource
from app.services.audit import write_log


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    except (TypeError, ValueError):
        return None


def _category_for_entry(db: Session, entry: dict) -> Category | None:
    tags = entry.get("tags") or []
    name = None
    if tags:
        name = tags[0].get("term")
    if not name:
        name = "Мир"
    category = db.query(Category).filter(Category.name == name[:100]).one_or_none()
    if category is None:
        category = Category(name=name[:100])
        db.add(category)
        db.flush()
    return category


def fetch_source(db: Session, source: NewsSource) -> int:
    if source.type != "rss":
        write_log(
            db,
            action="aggregate_skip",
            entity="news_sources",
            level="warning",
            message=f"Источник {source.name} имеет тип {source.type}; для API требуется адаптер.",
        )
        return 0

    response = httpx.get(source.url, timeout=20, follow_redirects=True)
    response.raise_for_status()
    feed = feedparser.parse(response.text)
    created = 0

    for entry in feed.entries[:30]:
        url = entry.get("link")
        title = (entry.get("title") or "").strip()
        if not url or not title:
            continue
        if db.query(NewsArticle).filter(NewsArticle.url == url).one_or_none():
            continue

        category = _category_for_entry(db, entry)
        content = (
            entry.get("summary")
            or entry.get("description")
            or entry.get("title")
            or "Описание новости отсутствует в RSS-ленте."
        )
        published_at = _parse_datetime(entry.get("published") or entry.get("updated"))
        db.add(
            NewsArticle(
                source_id=source.id,
                category_id=category.id if category else None,
                title=title[:500],
                content=content,
                url=url[:700],
                published_at=published_at,
                fetched_at=datetime.now(timezone.utc),
                category=category.name if category else None,
            )
        )
        created += 1

    db.commit()
    write_log(
        db,
        action="aggregate_source",
        entity="news_articles",
        message=f"Источник {source.name}: добавлено новостей {created}.",
    )
    return created


def fetch_all_sources(db: Session) -> dict[str, int]:
    result: dict[str, int] = {}
    sources = db.query(NewsSource).filter(NewsSource.is_active.is_(True)).all()
    for source in sources:
        try:
            result[source.name] = fetch_source(db, source)
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            result[source.name] = 0
            write_log(
                db,
                action="aggregate_error",
                entity="news_sources",
                level="error",
                message=f"Ошибка агрегации {source.name}: {exc}",
            )
    return result
