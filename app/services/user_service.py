from typing import List, Optional
from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate
from crud.user import crud_user


class UserService:
    def __init__(self):
        self.crud = crud_user

    def get(self, db: Session, id: int) -> Optional[User]:
        return self.crud.get(db, id)

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return self.crud.get_multi(db, skip=skip, limit=limit)

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return self.crud.get_by_username(db, username)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return self.crud.get_by_email(db, email)

    def get_active(self, db: Session) -> List[User]:
        return self.crud.get_active(db)

    def create(self, db: Session, obj_in: UserCreate) -> User:
        # Проверка уникальности
        if self.crud.get_by_username(db, obj_in.username):
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Username already exists")
        if self.crud.get_by_email(db, obj_in.email):
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Email already exists")
        return self.crud.create(db, obj_in)

    def update(self, db: Session, id: int, obj_in: UserUpdate) -> Optional[User]:
        return self.crud.update(db, id, obj_in)

    def delete(self, db: Session, id: int) -> Optional[User]:
        return self.crud.delete(db, id)

    def toggle_active(self, db: Session, id: int, is_active: bool) -> Optional[User]:
        return self.crud.toggle_active(db, id, is_active)


user_service = UserService()
