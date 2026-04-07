# crud/user.py
from sqlalchemy.orm import Session
from typing import Optional

from models.user import User
from schemas.user import UserCreate, UserUpdate


class CRUDUser:
    def __init__(self, model):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return db.query(self.model).filter(self.model.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Получить пользователя по username"""
        return db.query(self.model).filter(self.model.username == username).first()

    def create(self, db: Session, obj_in: UserCreate, hashed_password: str = None) -> User:
        """Создать пользователя"""
        db_obj = self.model(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=hashed_password,
            full_name=obj_in.full_name,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: User, obj_in: UserUpdate) -> User:
        """Обновить пользователя"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Optional[User]:
        """Удалить пользователя"""
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


# Создаем экземпляр


# Создаем экземпляр для использования
crud_user = CRUDUser(User)