import subprocess

from sqlalchemy.orm import Session

from app.services.audit import write_log


def apply_migrations(db: Session, user_id: int, ip_address: str | None = None) -> str:
    """Админский механизм обновления БД через Alembic."""
    result = subprocess.run(["alembic", "upgrade", "head"], check=True, capture_output=True, text=True, timeout=120)
    output = result.stdout or result.stderr or "Миграции применены."
    write_log(db, action="migrations_apply", entity="database", message=output, user_id=user_id, ip_address=ip_address)
    return output
