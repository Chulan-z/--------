from datetime import timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import aware_now, client_ip, get_current_user
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models.refresh_token import RefreshToken
from app.models.role import Role
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenPair
from app.schemas.common import Message
from app.schemas.user import UserOut
from app.services.audit import write_log

router = APIRouter(prefix="/auth", tags=["auth"])


def _save_refresh_token(db: Session, user_id: int, token: str) -> None:
    db.add(RefreshToken(user_id=user_id, token=token, expires_at=aware_now() + timedelta(days=settings.refresh_token_expire_days)))
    db.commit()


def _issue_pair(db: Session, user: User) -> TokenPair:
    access = create_access_token(user.id, user.role.name)
    refresh = create_refresh_token(user.id)
    _save_refresh_token(db, user.id, refresh)
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)) -> TokenPair:
    exists = db.query(User).filter(or_(User.email == payload.email, User.username == payload.username)).one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="Пользователь с таким email или именем уже существует")
    role = db.query(Role).filter(Role.name == "user").one()
    user = User(username=payload.username, email=payload.email, password_hash=get_password_hash(payload.password), role_id=role.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    write_log(db, action="register", entity="users", message=f"Зарегистрирован пользователь {user.email}.", user_id=user.id, ip_address=client_ip(request))
    return _issue_pair(db, user)


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenPair:
    user = db.query(User).filter(User.email == payload.email).one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        write_log(db, action="login_failed", entity="users", level="warning", message=f"Неудачный вход для {payload.email}.", ip_address=client_ip(request))
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Пользователь заблокирован")
    write_log(db, action="login", entity="users", message=f"Пользователь {user.email} вошел в систему.", user_id=user.id, ip_address=client_ip(request))
    return _issue_pair(db, user)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenPair:
    try:
        token_payload = jwt.decode(payload.refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        if token_payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Некорректный refresh token")
        user_id = int(token_payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Недействительный refresh token") from None
    stored = db.query(RefreshToken).filter(RefreshToken.token == payload.refresh_token, RefreshToken.revoked.is_(False)).one_or_none()
    if stored is None:
        raise HTTPException(status_code=401, detail="Refresh token истек или отозван")
    expires_at = stored.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < aware_now():
        raise HTTPException(status_code=401, detail="Refresh token истек или отозван")
    stored.revoked = True
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Пользователь неактивен")
    db.commit()
    return _issue_pair(db, user)


@router.post("/logout", response_model=Message)
def logout(payload: RefreshRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Message:
    stored = db.query(RefreshToken).filter(RefreshToken.token == payload.refresh_token, RefreshToken.user_id == current_user.id).one_or_none()
    if stored:
        stored.revoked = True
        db.commit()
    return Message(message="Выход выполнен")


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
