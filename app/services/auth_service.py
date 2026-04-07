from sqlalchemy.orm import Session
from fastapi import HTTPException
from crud.user import crud_user
from core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from schemas.user import UserCreate


class AuthService:
    def register(self, db: Session, user_data: UserCreate):
        # Проверка существования
        existing = user_crud.get_by_email(db, user_data.email)
        if existing:
            raise HTTPException(400, "Email already registered")

        # Создание пользователя
        hashed = get_password_hash(user_data.password)
        user = crud_user.create(db, user_data, hashed_password=hashed)

        return {
            "access_token": create_access_token(data={"sub": str(user.id)}),
            "refresh_token": create_refresh_token(data={"sub": str(user.id)}),
            "token_type": "bearer"
        }

    def login(self, db: Session, email: str, password: str):
        """Авторизация пользователя - ВОЗВРАЩАЕТ ПОЛЬЗОВАТЕЛЯ, а не токены"""
        # Поиск пользователя по email
        user = crud_user.get_by_email(db, email)

        # Проверка пароля
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(401, "Invalid email or password")

        # ВОЗВРАЩАЕМ ПОЛЬЗОВАТЕЛЯ, а не токены
        return user

    def refresh(self, db: Session, refresh_token: str):
        payload = decode_token(refresh_token, "refresh")
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(401, "Invalid refresh token")

        user = crud_user.get(db, int(user_id))
        if not user:
            raise HTTPException(401, "User not found")

        return {
            "access_token": create_access_token(data={"sub": str(user.id)}),
            "token_type": "bearer"
        }


auth_service = AuthService()