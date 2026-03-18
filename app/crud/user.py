from typing import List, Optional
from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CRUDUser:
    def get(self, db: Session, id: int) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_active(self, db: Session) -> List[User]:
        return db.query(User).filter(User.is_active == 1).all()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        hashed_password = pwd_context.hash(obj_in.password)
        db_user = User(
            username=obj_in.username,
            email=obj_in.email,
            full_name=obj_in.full_name,
            is_active=1
        )
        # Добавляем поле hashed_password если нужно в модели
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update(self, db: Session, id: int, obj_in: UserUpdate) -> Optional[User]:
        db_user = self.get(db, id)
        if db_user:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_user, field, value)
            db.commit()
            db.refresh(db_user)
        return db_user

    def delete(self, db: Session, id: int) -> Optional[User]:
        db_user = self.get(db, id)
        if db_user:
            db.delete(db_user)
            db.commit()
        return db_user

    def toggle_active(self, db: Session, id: int, is_active: bool) -> Optional[User]:
        db_user = self.get(db, id)
        if db_user:
            db_user.is_active = 1 if is_active else 0
            db.commit()
            db.refresh(db_user)
        return db_user


crud_user = CRUDUser()
