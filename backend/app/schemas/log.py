from datetime import datetime

from app.schemas.common import ORMModel


class LogOut(ORMModel):
    id: int
    user_id: int | None
    action: str
    entity: str
    level: str
    message: str
    ip_address: str | None
    created_at: datetime
