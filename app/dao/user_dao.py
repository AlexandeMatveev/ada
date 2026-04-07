from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import or_

from dao.base import BaseDAO
from models.user import User
from schemas.user import UserCreate, UserUpdate


class UserDAO(BaseDAO[User, UserCreate, UserUpdate]):
    """DAO для работы с пользователями"""

    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return db.query(self.model).filter(self.model.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Получить пользователя по username"""
        return db.query(self.model).filter(self.model.username == username).first()

    def get_by_email_or_username(
            self,
            db: Session,
            email: str,
            username: str
    ) -> Optional[User]:
        """Получить пользователя по email или username"""
        return db.query(self.model).filter(
            or_(
                self.model.email == email,
                self.model.username == username
            )
        ).first()

    def create_from_dict(self, db: Session, obj_data: dict) -> User:
        """Создать пользователя из словаря"""
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Создаем экземпляр для использования
user_dao = UserDAO()