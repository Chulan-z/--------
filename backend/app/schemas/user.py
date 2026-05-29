from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class RoleOut(ORMModel):
    id: int
    name: str
    permissions: list[str]


class UserOut(ORMModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime
    role: RoleOut


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=80)
    email: EmailStr | None = None
    is_active: bool | None = None
    role_id: int | None = None
