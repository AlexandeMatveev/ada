from sqlalchemy.orm import Session
from typing import List, Optional
from crud.user import user_crud
from schemas.user import UserCreate, UserUpdate, UserInDB


class UserService:
    def __init__(self):
        self.crud = user_crud

    def create(self, db: Session, obj_in: UserCreate) -> UserInDB:
        return self.crud.create(db, obj_in=obj_in)

    def get(self, db: Session, id: int) -> Optional[UserInDB]:
        return self.crud.get(db, id=id)

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        return self.crud.get_multi(db, skip=skip, limit=limit)

    def get_active(self, db: Session) -> List[UserInDB]:
        return self.crud.get_active(db)

    def update(self, db: Session, id: int, obj_in: UserUpdate) -> Optional[UserInDB]:
        return self.crud.update(db, id=id, obj_in=obj_in)

    def delete(self, db: Session, id: int) -> Optional[UserInDB]:
        return self.crud.delete(db, id=id)

    def toggle_active(self, db: Session, user_id: int, is_active: bool) -> Optional[UserInDB]:
        return self.crud.toggle_active(db, user_id, is_active)


user_service = UserService()