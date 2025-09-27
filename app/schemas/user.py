"""Pydantic‑схемы для пользователей."""
from __future__ import annotations

from pydantic import BaseModel

from app.models.user import UserRole


class UserOut(BaseModel):
    id: int
    telegram_id: int
    name: str | None
    role: int

    class Config:
        from_attributes = True


class UserMe(BaseModel):
    """Текущий пользователь (минимум данных)."""

    id: int
    telegram_id: int
    role: UserRole
