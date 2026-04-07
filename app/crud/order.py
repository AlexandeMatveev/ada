from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from crud.base import CRUDBase
from models.order import Order, OrderItem
from schemas.order import OrderCreate, OrderUpdate


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def get_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        return db.query(self.model).filter(
            self.model.user_id == user_id
        ).order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Order]:
        return db.query(self.model).filter(
            self.model.status == status
        ).order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()

    def get_user_order(self, db: Session, order_id: int, user_id: int) -> Optional[Order]:
        return db.query(self.model).filter(
            and_(
                self.model.id == order_id,
                self.model.user_id == user_id
            )
        ).first()

    def update_status(self, db: Session, order_id: int, status: str) -> Optional[Order]:
        order = self.get(db, order_id)
        if order:
            order.status = status
            db.commit()
            db.refresh(order)
        return order

    def create_from_dict(self, db: Session, obj_data: dict) -> Order:
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDOrderItem(CRUDBase[OrderItem, None, None]):
    def __init__(self):
        super().__init__(OrderItem)

    def create_from_dict(self, db: Session, obj_data: dict) -> OrderItem:
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_order(self, db: Session, order_id: int) -> List[OrderItem]:
        return db.query(self.model).filter(self.model.order_id == order_id).all()


crud_order = CRUDOrder(Order)
crud_order_item = CRUDOrderItem()