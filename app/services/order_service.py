# services/order_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

# Импортируем из crud вместо dao
from crud.item import crud_item
from crud.order import crud_order, crud_order_item
from models.order import OrderStatus
from schemas.order import OrderCreate, OrderUpdate


class OrderService:
    def create_order(self, db: Session, user_id: int, order_data: OrderCreate):
        """Создание нового заказа"""
        # Проверяем наличие товаров и считаем сумму
        total_amount = 0
        order_items_data = []

        for item_data in order_data.items:
            # Получаем товар из БД
            item = crud_item.get(db, item_data.item_id)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item {item_data.item_id} not found"
                )

            # Проверяем доступность
            if not hasattr(item, 'is_available') or item.is_available:
                # Если нет поля is_available, пропускаем проверку
                pass

            # Проверяем наличие на складе (если есть поле stock)
            if hasattr(item, 'stock') and item.stock < item_data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough stock for {item.title}. Available: {item.stock}"
                )

            # Считаем сумму (если есть поле price)
            price = getattr(item, 'price', 0)
            total_amount += price * item_data.quantity

            # Сохраняем данные для создания позиции заказа
            order_items_data.append({
                "item_id": item.id,
                "quantity": item_data.quantity,
                "price_at_time": price,
                "item_title": item.title
            })

        # Создаем заказ
        order_dict = order_data.model_dump()
        order_dict["user_id"] = user_id
        order_dict["total_amount"] = total_amount
        order_dict["status"] = OrderStatus.PENDING

        order = crud_order.create_from_dict(db, order_dict)

        # Создаем позиции заказа
        for item_data in order_items_data:
            crud_order_item.create_from_dict(db, {
                **item_data,
                "order_id": order.id
            })

        # Уменьшаем количество товаров на складе (если есть поле stock)
        for item_data in order_data.items:
            item = crud_item.get(db, item_data.item_id)
            if hasattr(item, 'stock'):
                new_stock = item.stock - item_data.quantity
                crud_item.update(db, item.id, {"stock": new_stock})

        return self.get_order(db, order.id, user_id)

    def get_order(self, db: Session, order_id: int, user_id: int):
        """Получение заказа по ID"""
        order = crud_order.get_user_order(db, order_id, user_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        return order

    def get_user_orders(self, db: Session, user_id: int, skip: int = 0, limit: int = 100):
        """Получение всех заказов пользователя"""
        orders = crud_order.get_by_user(db, user_id, skip, limit)
        return orders

    def get_all_orders(self, db: Session, skip: int = 0, limit: int = 100, status: str = None):
        """Получение всех заказов (только для админа)"""
        if status:
            return crud_order.get_by_status(db, status, skip, limit)
        return crud_order.get_multi(db, skip, limit)

    def update_order_status(self, db: Session, order_id: int, status: str):
        """Обновление статуса заказа (только для админа)"""
        order = crud_order.get(db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        return crud_order.update_status(db, order_id, status)

    def cancel_order(self, db: Session, order_id: int, user_id: int):
        """Отмена заказа пользователем"""
        order = crud_order.get_user_order(db, order_id, user_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel order with status {order.status}"
            )

        # Возвращаем товары на склад
        for item in order.items:
            if hasattr(item, 'item_id'):
                item_obj = crud_item.get(db, item.item_id)
                if item_obj and hasattr(item_obj, 'stock'):
                    new_stock = item_obj.stock + item.quantity
                    crud_item.update(db, item_obj.id, {"stock": new_stock})

        return crud_order.update_status(db, order_id, OrderStatus.CANCELLED)


order_service = OrderService()