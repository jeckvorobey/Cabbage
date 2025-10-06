"""Pydantic‑схемы для товаров, цен и изображений."""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class ProductImageBase(BaseModel):
    """Базовые поля изображения товара."""
    file_path: str
    is_primary: bool = False
    sort_order: int = 0


class ProductImageOut(ProductImageBase):
    """DTO изображения товара."""
    id: int
    product_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProductIn(BaseModel):
    """Схема для создания товара."""
    name: str
    category_id: int
    unit_id: int
    qty: int = Field(ge=0, description="Остаток в граммах")
    description: str | None = None


class ProductUpdate(BaseModel):
    """Схема для обновления товара."""
    name: str | None = None
    category_id: int | None = None
    unit_id: int | None = None
    qty: int | None = Field(default=None, ge=0, description="Остаток в граммах")
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
    primary_image: str | None = Field(default=None, description="Абсолютный URL главного изображения")
    images: list[ProductImageOut] | None = None

    class Config:
        from_attributes = True
