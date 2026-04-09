from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from core.dependencies import get_current_user, get_current_superuser
from services.order_service import order_service
from schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderListResponse
from models.user import User

router = APIRouter()

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await order_service.create_order(db, current_user.id, order_data)


@router.get("/", response_model=List[OrderListResponse])
def get_my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение всех заказов текущего пользователя"""
    orders = order_service.get_user_orders(db, current_user.id, skip, limit)
    # Форматируем ответ с количеством товаров
    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "user_id": order.user_id,
            "status": order.status,
            "total_amount": order.total_amount,
            "created_at": order.created_at,
            "items_count": len(order.items)
        })
    return result

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение конкретного заказа"""
    return order_service.get_order(db, order_id, current_user.id)

@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отмена заказа"""
    return order_service.cancel_order(db, order_id, current_user.id)

# Админские эндпоинты
@router.get("/admin/all", response_model=List[OrderResponse])
def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None, regex="^(pending|confirmed|processing|shipped|delivered|cancelled)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Получение всех заказов (только админ)"""
    return order_service.get_all_orders(db, skip, limit, status)

@router.put("/admin/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Обновление статуса заказа (только админ)"""
    return order_service.update_order_status(db, order_id, status_data.status)