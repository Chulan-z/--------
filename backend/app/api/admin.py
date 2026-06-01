from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import client_ip, get_current_admin
from app.db.session import get_db
from app.models.backup import Backup
from app.models.log import Log
from app.models.role import Role
from app.models.user import User
from app.schemas.backup import BackupOut, RestoreRequest
from app.schemas.common import Message
from app.schemas.log import LogOut
from app.schemas.user import RoleOut, UserOut, UserUpdate
from app.services.backup import create_backup, restore_backup
from app.services.migrations import apply_migrations

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[User]:
    return db.query(User).order_by(User.id).all()


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if payload.role_id is not None and db.get(Role, payload.role_id) is None:
        raise HTTPException(status_code=400, detail="Роль не найдена")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


@router.get("/roles", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[Role]:
    return db.query(Role).order_by(Role.id).all()


@router.get("/logs", response_model=list[LogOut])
def list_logs(db: Session = Depends(get_db), _: User = Depends(get_current_admin), limit: int = 100) -> list[Log]:
    return db.query(Log).order_by(Log.created_at.desc()).limit(min(limit, 500)).all()


@router.get("/backups", response_model=list[BackupOut])
def list_backups(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[Backup]:
    return db.query(Backup).order_by(Backup.created_at.desc()).all()


@router.post("/backups", response_model=BackupOut, status_code=201)
def make_backup(request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)) -> Backup:
    return create_backup(db, user_id=admin.id, ip_address=client_ip(request))


@router.post("/backups/restore", response_model=BackupOut)
def restore(request_payload: RestoreRequest, request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)) -> Backup:
    try:
        return restore_backup(db, request_payload.filename, user_id=admin.id, ip_address=client_ip(request))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/migrations", response_model=Message)
def run_migrations(request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)) -> Message:
    output = apply_migrations(db, admin.id, client_ip(request))
    return Message(message=output)
