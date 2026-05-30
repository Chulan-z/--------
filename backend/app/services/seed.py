from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.category import Category
from app.models.role import Role
from app.models.source import NewsSource
from app.models.user import User


ROLE_PERMISSIONS = {
    "user": ["news:read", "profile:read", "profile:update"],
    "admin": [
        "news:read",
        "profile:read",
        "profile:update",
        "users:manage",
        "sources:manage",
        "logs:read",
        "backups:manage",
        "migrations:apply",
    ],
}

DEFAULT_CATEGORIES = ["Мир", "Технологии", "Экономика", "Наука", "Спорт", "Культура"]

DEFAULT_SOURCES = [
    {
        "name": "BBC World",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "type": "rss",
    },
    {
        "name": "NASA Breaking News",
        "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
        "type": "rss",
    },
    {
        "name": "Hacker News",
        "url": "https://hnrss.org/frontpage",
        "type": "rss",
    },
]


def seed_data(db: Session) -> None:
    for role_name, permissions in ROLE_PERMISSIONS.items():
        role = db.query(Role).filter(Role.name == role_name).one_or_none()
        if role is None:
            db.add(Role(name=role_name, permissions=permissions))
        else:
            role.permissions = permissions
    db.commit()

    for category_name in DEFAULT_CATEGORIES:
        if db.query(Category).filter(Category.name == category_name).one_or_none() is None:
            db.add(Category(name=category_name))
    db.commit()

    for source_data in DEFAULT_SOURCES:
        if db.query(NewsSource).filter(NewsSource.url == source_data["url"]).one_or_none() is None:
            db.add(NewsSource(**source_data, is_active=True))
    db.commit()

    admin_role = db.query(Role).filter(Role.name == "admin").one()
    admin = db.query(User).filter(User.email == settings.first_admin_email).one_or_none()
    if admin is None:
        db.add(
            User(
                username=settings.first_admin_username,
                email=settings.first_admin_email,
                password_hash=get_password_hash(settings.first_admin_password),
                role_id=admin_role.id,
                is_active=True,
            )
        )
        db.commit()
