from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user, create_access_token, create_refresh_token
from schemas.user import UserCreate
from schemas.a_tokens import LoginRequest, RefreshTokenRequest
from services.auth_service import auth_service
from models.user import User

router = APIRouter(tags=["auth"])


@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация - возвращает токены"""
    return auth_service.register(db, user_data)


@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Вход - возвращает токены"""
    # auth_service.login возвращает пользователя
    user = auth_service.login(db, login_data.email, login_data.password)

    # Создаем токены здесь
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
def refresh(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Обновление access токена"""
    return auth_service.refresh(db, refresh_data.refresh_token)


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Получить текущего пользователя"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name
    }


@router.post("/logout")
def logout():
    """Выход - удалите токены на клиенте"""
    return {"message": "Successfully logged out"}