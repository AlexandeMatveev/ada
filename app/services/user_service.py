from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import re

from services.base import BaseService
from crud.user import crud_user
from schemas.user import UserCreate, UserUpdate
from models.user import User
from core.security import get_password_hash, verify_password  # <-- импорт из security


class UserService(BaseService[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(crud_user)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return crud_user.get_by_email(db, email=email)

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return crud_user.get_by_username(db, username=username)

    def get_active(self, db: Session) -> List[User]:
        pass

    def toggle_active(self, db: Session, user_id: int, active: bool) -> User:
        pass
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Создаёт пользователя с хешированием пароля"""
        self._validate_create(db, obj_in)
        hashed_password = get_password_hash(obj_in.password)
        return crud_user.create(db, obj_in=obj_in, hashed_password=hashed_password)

    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, username) or self.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def _validate_email(self, email: str) -> bool:
        return bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', email))

    def _validate_username(self, username: str) -> bool:
        return bool(re.match(r'^[a-zA-Z0-9_]{3,50}$', username))

    def _validate_create(self, db: Session, obj_in: UserCreate) -> None:
        if not self._validate_email(obj_in.email):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid email format")
        if not self._validate_username(obj_in.username):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username must be 3-50 chars: letters, numbers, _")
        if self.get_by_email(db, obj_in.email):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
        if self.get_by_username(db, obj_in.username):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username already taken")

    def _validate_update(self, db: Session, db_obj: User, obj_in: UserUpdate) -> None:
        if obj_in.email and obj_in.email != db_obj.email:
            if not self._validate_email(obj_in.email):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid email format")
            if self.get_by_email(db, obj_in.email):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

        if obj_in.username and obj_in.username != db_obj.username:
            if not self._validate_username(obj_in.username):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username must be 3-50 chars: letters, numbers, _")
            if self.get_by_username(db, obj_in.username):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username already taken")

    def _validate_delete(self, db: Session, db_obj: User) -> None:
        if db_obj.username == "admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot delete admin user")


user_service = UserService()