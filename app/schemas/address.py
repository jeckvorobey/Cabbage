"""Pydantic‑схемы для адресов пользователя."""
from __future__ import annotations

from pydantic import BaseModel, Field


class AddressCreate(BaseModel):
    """Создание адреса: строка адреса и опциональный комментарий, флаг по умолчанию."""

    address_line: str = Field(min_length=3, max_length=255)
    comment: str | None = Field(default=None, max_length=255)
    is_default: bool = False


class AddressUpdate(BaseModel):
    """Частичное обновление адреса."""

    address_line: str | None = Field(default=None, min_length=3, max_length=255)
    comment: str | None = Field(default=None, max_length=255)
    is_default: bool | None = None


class AddressOut(BaseModel):
    """DTO адреса для ответов API."""

    id: int
    address_line: str
    comment: str | None
    is_default: bool

    class Config:
        from_attributes = True
