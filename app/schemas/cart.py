from __future__ import annotations

from pydantic import BaseModel, Field


class CartItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class CartItemOut(BaseModel):
    product_id: int
    quantity: int
    name: str
    unit_symbol: str
    price: float | None = None
    line_total: float | None = None


class CartOut(BaseModel):
    items: list[CartItemOut]
    total: float
