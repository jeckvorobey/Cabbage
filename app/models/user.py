"""Модель пользователя и связанные сущности."""
from __future__ import annotations

from datetime import datetime
from enum import IntEnum

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class UserRole(IntEnum):
    """Роли пользователей (меньше число — больше прав)."""

    ADMIN = 1
    MANAGER = 2
    CUSTOMER = 9


class User(Base):
    """Пользователь приложения, идентифицируемый по Telegram ID.

    Поле ``role`` хранит уровень доступа согласно ``UserRole``.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), default=None)
    username: Mapped[str | None] = mapped_column(String(255), default=None)
    first_name: Mapped[str | None] = mapped_column(String(255), default=None)
    last_name: Mapped[str | None] = mapped_column(String(255), default=None)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False)
    language_code: Mapped[str | None] = mapped_column(String(16), default=None)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    phone_email: Mapped[str | None] = mapped_column(String(255), default=None)
    role: Mapped[int] = mapped_column(Integer, default=UserRole.CUSTOMER.value)
    subscribe_news: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # отношения
    addresses: Mapped[list["Address"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class Address(Base):
    """Адрес доставки пользователя."""

    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    address_line: Mapped[str] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(120), default=None)
    comment: Mapped[str | None] = mapped_column(String(255), default=None)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[User] = relationship(back_populates="addresses")
