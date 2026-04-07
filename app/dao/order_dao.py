from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from dao.base import BaseDAO
from models.order import Order, OrderItem
from schemas.order import OrderCreate, OrderUpdate


class OrderDAO(BaseDAO[Order, OrderCreate, OrderUpdate]):
    def __init__(self):
        super().__init__(Order)

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


class OrderItemDAO(BaseDAO[OrderItem, None, None]):
    def __init__(self):
        super().__init__(OrderItem)

    def create_items(self, db: Session, items: list, order_id: int) -> List[OrderItem]:
        order_items = []
        for item in items:
            db_item = OrderItem(
                order_id=order_id,
                item_id=item.item_id,
                quantity=item.quantity,
                price_at_time=item.price_at_time,
                item_title=item.item_title
            )
            db.add(db_item)
            order_items.append(db_item)
        db.commit()
        for item in order_items:
            db.refresh(item)
        return order_items


order_dao = OrderDAO()
order_item_dao = OrderItemDAO()