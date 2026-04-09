import asyncio
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from crud.item import crud_item
from crud.order import crud_order, crud_order_item
from models.order import OrderStatus
from schemas.order import OrderCreate, OrderUpdate
from schemas.item import ItemUpdate
from core.rabbitmq import rabbit_client


class OrderService:
    async def create_order(self, db: Session, user_id: int, order_data: OrderCreate):
        total_amount = 0
        order_items_data = []

        for item_data in order_data.items:
            item = crud_item.get(db, item_data.item_id)
            if not item:
                raise HTTPException(status_code=404, detail=f"Item {item_data.item_id} not found")

            stock = getattr(item, 'stock', 0) or 0
            if stock < item_data.quantity:
                raise HTTPException(status_code=400, detail=f"Not enough stock for {item.title}. Available: {stock}")

            price = getattr(item, 'price', 0) or 0
            total_amount += price * item_data.quantity

            order_items_data.append({
                "item_id": item.id,
                "quantity": item_data.quantity,
                "price_at_time": price,
                "item_title": item.title
            })

        # Создаём заказ (исключаем items из словаря)
        order_dict = order_data.model_dump(exclude={'items'})
        order_dict["user_id"] = user_id
        order_dict["total_amount"] = total_amount
        order_dict["status"] = OrderStatus.PENDING

        order = crud_order.create_from_dict(db, order_dict)

        # Создаём позиции заказа
        for item_data in order_items_data:
            crud_order_item.create_from_dict(db, {**item_data, "order_id": order.id})

        # Уменьшаем остатки на складе
        for item_data in order_data.items:
            item = crud_item.get(db, item_data.item_id)
            if hasattr(item, 'stock'):
                new_stock = item.stock - item_data.quantity
                item_update = ItemUpdate(stock=new_stock)
                crud_item.update(db, item.id, item_update)

        # Отправка события в RabbitMQ (не блокирует ответ)
        asyncio.create_task(
            rabbit_client.publish("order.created", {
                "order_id": order.id,
                "user_id": user_id,
                "total_amount": total_amount,
                "items": order_items_data
            })
        )

        return self.get_order(db, order.id, user_id)

    def get_order(self, db: Session, order_id: int, user_id: int):
        order = crud_order.get_user_order(db, order_id, user_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    def get_user_orders(self, db: Session, user_id: int, skip: int = 0, limit: int = 100):
        return crud_order.get_by_user(db, user_id, skip, limit)

    def get_all_orders(self, db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None):
        if status:
            return crud_order.get_by_status(db, status, skip, limit)
        return crud_order.get_multi(db, skip, limit)

    def update_order_status(self, db: Session, order_id: int, new_status: str):
        order = crud_order.get(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return crud_order.update_status(db, order_id, new_status)

    def cancel_order(self, db: Session, order_id: int, user_id: int):
        order = crud_order.get_user_order(db, order_id, user_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise HTTPException(status_code=400, detail=f"Cannot cancel order with status {order.status}")
        for item in order.items:
            item_obj = crud_item.get(db, item.item_id)
            if item_obj and hasattr(item_obj, 'stock'):
                new_stock = item_obj.stock + item.quantity
                item_update = ItemUpdate(stock=new_stock)
                crud_item.update(db, item_obj.id, item_update)
        return crud_order.update_status(db, order_id, OrderStatus.CANCELLED)


order_service = OrderService()