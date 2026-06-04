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

DEFAULT_CATEGORIES = [
    "\u0412\u0430\u0436\u043d\u0430\u044f",
    "\u041c\u0438\u0440",
    "\u041f\u0440\u043e\u0438\u0441\u0448\u0435\u0441\u0442\u0432\u0438\u044f",
    "\u0413\u043e\u0440\u043e\u0434",
    "\u041e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u0435",
    "\u0422\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0438",
    "\u0421\u043f\u043e\u0440\u0442",
    "\u041a\u0443\u043b\u044c\u0442\u0443\u0440\u0430",
]

DEFAULT_SOURCES = [
    {
        "name": "\u0420\u0435\u0434\u0430\u043a\u0446\u0438\u044f \u0430\u0433\u0440\u0435\u0433\u0430\u0442\u043e\u0440\u0430",
        "url": "https://local.news/manual",
        "type": "api",
        "is_active": False,
    },
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
        source = db.query(NewsSource).filter(NewsSource.url == source_data["url"]).one_or_none()
        if source is None:
            data = source_data.copy()
            is_active = data.pop("is_active", True)
            db.add(NewsSource(**data, is_active=is_active))
        else:
            source.name = source_data["name"]
            source.type = source_data["type"]
            source.is_active = source_data.get("is_active", source.is_active)
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
