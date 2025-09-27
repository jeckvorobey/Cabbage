"""Pydantic‑схемы для заказов."""
from __future__ import annotations

from datetime import datetime
from typing import Sequence

from pydantic import BaseModel, Field

from app.models.order import OrderStatus


class OrderItemIn(BaseModel):
    """Позиция заказа на вход: id товара и количество."""

    product_id: int = Field(gt=0)
    quantity: float = Field(gt=0)


class OrderCreate(BaseModel):
    """Входная схема создания заказа."""

    items: Sequence[OrderItemIn]
    delivery_type: str = Field(default="delivery")  # delivery | pickup
    address_id: int | None = None
    payment_method: str | None = None


class OrderItemOut(BaseModel):
    product_id: int
    quantity: float
    price: float


class OrderOut(BaseModel):
    id: int
    order_date: datetime
    status: OrderStatus
    is_paid: bool
    delivery_type: str
    address_id: int | None
    total_amount: float | None
    items: list[OrderItemOut]

    class Config:
        from_attributes = True
