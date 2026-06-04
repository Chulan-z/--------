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


def test_admin_can_create_featured_article_with_image(client):
    login = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "admin12345"})
    token = login.json()["access_token"]
    created = client.post(
        "/api/admin/articles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Своя главная новость",
            "content": "Текст новости, добавленной администратором вручную.",
            "category": "Важная",
            "image_url": "https://example.com/news.jpg",
            "is_featured": True,
        },
    )

    assert created.status_code == 201
    assert created.json()["image_url"] == "https://example.com/news.jpg"
    assert created.json()["is_featured"] is True

    feed = client.get("/api/articles")
    assert feed.status_code == 200
    assert feed.json()[0]["title"] == "Своя главная новость"


def test_admin_article_requires_title_and_content(client):
    login = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "admin12345"})
    token = login.json()["access_token"]
    response = client.post(
        "/api/admin/articles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "     ",
            "content": "     ",
            "category": "Важная",
            "is_featured": True,
        },
    )

    assert response.status_code == 422
