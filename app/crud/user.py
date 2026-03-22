from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate


class CRUDUser:
    def __init__(self):
        self.model = User

    def get(self, db: Session, user_id: int):
        """Получить пользователя по ID"""
        return db.query(self.model).filter(self.model.id == user_id).first()

    def get_by_email(self, db: Session, email: str):
        """Получить пользователя по email"""
        return db.query(self.model).filter(self.model.email == email).first()

    def create(self, db: Session, obj_in: UserCreate):
        """Создать пользователя"""
        db_obj = self.model(
            email=obj_in.email,
            username=obj_in.username,

        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: User, obj_in: UserUpdate):
        """Обновить пользователя"""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, user_id: int):
        """Удалить пользователя"""
        db_obj = db.query(self.model).get(user_id)
        db.delete(db_obj)
        db.commit()
        return db_obj


# Создаем экземпляр для использования
user_crud = CRUDUser()