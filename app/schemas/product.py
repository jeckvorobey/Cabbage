"""Pydantic‑схемы для товаров и цен."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ProductOut(BaseModel):
    """DTO для выдачи товара в каталоге с актуальной ценой."""

    id: int
    name: str
    category_id: int
    unit_symbol: str = Field(description="Краткое обозначение единицы (например, кг, шт)")
    price: float
    old_price: float | None = None
    stock_quantity: float

    class Config:
        from_attributes = True
