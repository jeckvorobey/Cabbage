"""Pydantic‑схемы для товаров и цен."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ProductIn(BaseModel):
    """Схема для создания товара."""
    name: str
    category_id: int
    unit_id: int
    qty: int = Field(ge=0, description="Остаток в граммах")
    image_url: str | None = None
    description: str | None = None


class ProductUpdate(BaseModel):
    """Схема для обновления товара."""
    name: str | None = None
    category_id: int | None = None
    unit_id: int | None = None
    qty: int | None = Field(default=None, ge=0, description="Остаток в граммах")
    image_url: str | None = None
    description: str | None = None


class ProductOut(BaseModel):
    """DTO для выдачи товара в каталоге с актуальной ценой."""

    id: int
    name: str
    category_id: int
    unit_symbol: str = Field(description="Краткое обозначение единицы (например, кг, шт)")
    price: float
    old_price: float | None = None
    qty: int

    class Config:
        from_attributes = True
