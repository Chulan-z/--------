from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.common import ORMModel


class CategoryOut(ORMModel):
    id: int
    name: str


class SourceOut(ORMModel):
    id: int
    name: str
    url: str
    type: str
    is_active: bool
    created_at: datetime


class SourceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    url: HttpUrl
    type: str = Field(pattern="^(rss|api)$")
    is_active: bool = True


class SourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    url: HttpUrl | None = None
    type: str | None = Field(default=None, pattern="^(rss|api)$")
    is_active: bool | None = None


class ArticleOut(ORMModel):
    id: int
    title: str
    content: str
    url: str
    published_at: datetime | None
    fetched_at: datetime
    category: str | None
    source: SourceOut
    category_ref: CategoryOut | None
