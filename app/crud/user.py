from sqlalchemy.orm import Session
from typing import List, Optional
from models.user import User
from schemas.user import UserCreate, UserUpdate


class CRUDUser:
    def __init__(self):
        self.model = User

    def get(self, db: Session, id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return db.query(self.model).filter(self.model.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Получить пользователя по username"""
        return db.query(self.model).filter(self.model.username == username).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить список пользователей"""
        return db.query(self.model).offset(skip).limit(limit).all()

    def get_active(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить только активных пользователей"""
        return db.query(self.model).filter(self.model.is_active == True).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        """Создать пользователя"""
        db_obj = self.model(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=obj_in.hashed_password if hasattr(obj_in, 'hashed_password') else None,
           
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, id: int, obj_in: UserUpdate) -> Optional[User]:
        """Обновить пользователя"""
        db_obj = self.get(db, id=id)
        if db_obj:
            update_data = obj_in.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Optional[User]:
        """Удалить пользователя"""
        db_obj = self.get(db, id=id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

    def toggle_active(self, db: Session, user_id: int, is_active: bool) -> Optional[User]:
        """Активировать/деактивировать пользователя"""
        db_obj = self.get(db, id=user_id)
        if db_obj:
            db_obj.is_active = is_active
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj


# Создаем экземпляр для использования
crud_user = CRUDUser()