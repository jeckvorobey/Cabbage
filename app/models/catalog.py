"""Модели каталога товаров: категории, единицы, продукты, цены."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Category(Base):
    """Категория товара (возможна вложенность через parent_id)."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    parent_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, default=None)

    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Unit(Base):
    """Единица измерения (кг, г, шт и т.д.)."""

    __tablename__ = "units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)
    symbol: Mapped[str] = mapped_column(String(16))

    products: Mapped[list["Product"]] = relationship(back_populates="unit")


class Product(Base):
    """Товар каталога."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    origin_country: Mapped[str | None] = mapped_column(String(120), default=None)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"))
    image_url: Mapped[str | None] = mapped_column(String(500), default=None)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    stock_quantity: Mapped[float] = mapped_column(Numeric(12, 3), default=0)

    category: Mapped[Category] = relationship(back_populates="products")
    unit: Mapped[Unit] = relationship(back_populates="products")
    prices: Mapped[list["Price"]] = relationship(back_populates="product", cascade="all, delete-orphan")


class Price(Base):
    """Цена товара. Предполагается одна текущая цена на товар (is_current=True)."""

    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    price: Mapped[float] = mapped_column(Numeric(12, 2))
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    old_price: Mapped[float | None] = mapped_column(Numeric(12, 2), default=None)

    product: Mapped[Product] = relationship(back_populates="prices")
