from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, field_validator

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
    image_url: str | None
    is_featured: bool
    published_at: datetime | None
    fetched_at: datetime
    category: str | None
    source: SourceOut
    category_ref: CategoryOut | None


class ArticleCreate(BaseModel):
    title: str = Field(min_length=5, max_length=500)
    content: str = Field(min_length=10)
    url: HttpUrl | None = None
    image_url: HttpUrl | None = None
    category: str = Field(default="Важная", min_length=2, max_length=100)
    source_id: int | None = None
    published_at: datetime | None = None
    is_featured: bool = True

    @field_validator("title", "content", "category")
    @classmethod
    def strip_and_require_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Поле обязательно для заполнения")
        return value


class ArticleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=5, max_length=500)
    content: str | None = Field(default=None, min_length=10)
    url: HttpUrl | None = None
    image_url: HttpUrl | None = None
    category: str | None = Field(default=None, min_length=2, max_length=100)
    source_id: int | None = None
    published_at: datetime | None = None
    is_featured: bool | None = None

    @field_validator("title", "content", "category")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Поле обязательно для заполнения")
        return value
