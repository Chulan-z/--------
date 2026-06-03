import os
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.backup import Backup
from app.services.audit import write_log


def _postgres_env_and_args() -> tuple[dict[str, str], dict[str, str]]:
    parsed = urlparse(settings.database_url.replace("postgresql+psycopg", "postgresql"))
    env = os.environ.copy()
    if parsed.password:
        env["PGPASSWORD"] = parsed.password
    args = {
        "host": parsed.hostname or "localhost",
        "port": str(parsed.port or 5432),
        "user": parsed.username or "postgres",
        "dbname": parsed.path.lstrip("/"),
    }
    return env, args


def create_backup(db: Session, user_id: int | None = None, ip_address: str | None = None) -> Backup:
    backup_dir = Path(settings.backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dump"
    path = backup_dir / filename
    env, args = _postgres_env_and_args()
    command = [
        "pg_dump",
        "-Fc",
        "-h",
        args["host"],
        "-p",
        args["port"],
        "-U",
        args["user"],
        "-f",
        str(path),
        args["dbname"],
    ]
    backup = Backup(filename=filename, size=0, status="failed")
    db.add(backup)
    db.commit()
    try:
        subprocess.run(command, env=env, check=True, capture_output=True, text=True, timeout=120)
        backup.size = path.stat().st_size
        backup.status = "created"
        db.commit()
        write_log(db, action="backup_create", entity="backups", message=f"Создана резервная копия {filename}.", user_id=user_id, ip_address=ip_address)
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        backup.status = "failed"
        db.commit()
        write_log(db, action="backup_error", entity="backups", level="error", message=f"Ошибка резервного копирования: {exc}", user_id=user_id, ip_address=ip_address)
        raise
    db.refresh(backup)
    return backup


def restore_backup(db: Session, filename: str, user_id: int | None = None, ip_address: str | None = None) -> Backup:
    path = Path(settings.backup_dir) / filename
    if not path.exists():
        raise FileNotFoundError(f"Файл резервной копии не найден: {filename}")
    env, args = _postgres_env_and_args()
    command = [
        "pg_restore",
        "--clean",
        "--if-exists",
        "-h",
        args["host"],
        "-p",
        args["port"],
        "-U",
        args["user"],
        "-d",
        args["dbname"],
        str(path),
    ]
    subprocess.run(command, env=env, check=True, capture_output=True, text=True, timeout=120)
    backup = db.query(Backup).filter(Backup.filename == filename).one_or_none()
    if backup is None:
        backup = Backup(filename=filename, size=path.stat().st_size, status="restored")
        db.add(backup)
    else:
        backup.status = "restored"
    db.commit()
    db.refresh(backup)
    write_log(db, action="backup_restore", entity="backups", message=f"Восстановлена резервная копия {filename}.", user_id=user_id, ip_address=ip_address)
    return backup
