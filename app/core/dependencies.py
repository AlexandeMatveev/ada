# app/core/dependencies.py
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from core.database import get_db
from core.config import settings
from core.security import decode_token
from models.user import User

# HTTP Bearer security
security = HTTPBearer()


def get_db_session(db: Session = Depends(get_db)) -> Session:
    """Базовое получение сессии БД"""
    return db


def get_token(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Извлечение токена из заголовка Authorization"""
    return credentials.credentials


def get_current_user(
        token: str = Depends(get_token),
        db: Session = Depends(get_db_session)
) -> User:
    """Получение текущего пользователя из токена"""
    try:
        payload = decode_token(token)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def get_current_superuser(
        current_user: User = Depends(get_current_user)
) -> User:
    """Проверка прав суперпользователя"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_current_user_optional(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db_session)
) -> Optional[User]:
    """Получение пользователя, если токен предоставлен (без ошибки)"""
    if not credentials:
        return None

    try:
        payload = decode_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id:
            return db.query(User).filter(User.id == user_id).first()
    except JWTError:
        pass

    return None