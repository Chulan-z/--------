from datetime import datetime

from app.schemas.common import ORMModel


class BackupOut(ORMModel):
    id: int
    filename: str
    created_at: datetime
    size: int
    status: str


class RestoreRequest(ORMModel):
    filename: str
