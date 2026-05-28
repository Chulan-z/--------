from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class NewsSource(Base):
    __tablename__ = "news_sources"
    __table_args__ = (CheckConstraint("type in ('rss', 'api')", name="ck_news_sources_type"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    articles = relationship("NewsArticle", back_populates="source", cascade="all, delete-orphan")
