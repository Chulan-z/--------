from datetime import datetime, timezone

from app.models.article import NewsArticle
from app.models.category import Category
from app.models.source import NewsSource


def test_article_feed_filters_by_query(client, db_session):
    category = Category(name="Тест")
    source = NewsSource(name="Local", url="https://local.test/rss", type="rss")
    db_session.add_all([category, source])
    db_session.flush()
    db_session.add(
        NewsArticle(
            source_id=source.id,
            category_id=category.id,
            title="Angular и FastAPI в учебной практике",
            content="Материал про интеграцию.",
            url="https://local.test/article-1",
            published_at=datetime.now(timezone.utc),
            category=category.name,
        )
    )
    db_session.commit()

    response = client.get("/api/articles?q=FastAPI")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["source"]["name"] == "Local"
