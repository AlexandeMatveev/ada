from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# Базовые схемы
class OrderItemBase(BaseModel):
    item_id: int
    quantity: int = Field(..., gt=0, le=999)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: int
    price_at_time: float
    item_title: str

    class Config:
        from_attributes = True


# Схемы заказов
class OrderBase(BaseModel):
    shipping_address: str = Field(..., min_length=5, max_length=500)
    phone: str = Field(..., pattern=r'^\+?[0-9]{10,15}$')
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    status: Optional[OrderStatusEnum] = None
    shipping_address: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class OrderResponse(OrderBase):
    id: int
    user_id: int
    status: OrderStatusEnum
    total_amount: float
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    id: int
    user_id: int
    status: OrderStatusEnum
    total_amount: float
    created_at: datetime
    items_count: int

    class Config:
        from_attributes = True