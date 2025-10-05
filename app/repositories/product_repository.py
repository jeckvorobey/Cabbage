"""Репозиторий товаров и цен."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.catalog import Price, Product, Unit, Category
from .base import BaseRepository


class ProductRepository(BaseRepository):
    """Запросы каталога с актуальными ценами и CRUD-операции."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _select_with_current_price(self) -> Select:
        p = aliased(Product)
        pr = aliased(Price)
        u = aliased(Unit)
        return (
            select(
                p.id,
                p.name,
                p.category_id,
                u.symbol.label("unit_symbol"),
                pr.price.label("price"),
                pr.old_price.label("old_price"),
                p.qty,
            )
            .join(pr, pr.product_id == p.id)
            .join(u, u.id == p.unit_id)
            .where(pr.is_current.is_(True))
            .order_by(p.id)
        )

    async def list_with_price(self) -> list[dict]:
        """Список товаров с актуальной ценой и единицей измерения.

        Возвращает словари, удобные для последующей валидации схемой ProductOut.
        """
        stmt = self._select_with_current_price()
        res = await self.session.execute(stmt)
        rows = res.mappings().all()
        return [dict(r) for r in rows]

    async def get_price_for_product(self, product_id: int) -> float | None:
        """Получить текущую цену товара по id, если есть."""
        stmt = (
            select(Price.price)
            .where(Price.product_id == product_id)
            .where(Price.is_current.is_(True))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    # --- CRUD продуктов ---
    async def create(self, data: dict) -> Product:
        # Проверки связей
        if not (await self.session.execute(select(Category).where(Category.id == data["category_id"]))).scalar_one_or_none():
            raise ValueError("Категория не найдена")
        if not (await self.session.execute(select(Unit).where(Unit.id == data["unit_id"]))).scalar_one_or_none():
            raise ValueError("Единица измерения не найдена")
        p = Product(**data)
        self.session.add(p)
        await self.session.flush()
        return p

    async def update(self, product: Product, data: dict) -> Product:
        if "category_id" in data:
            if not (await self.session.execute(select(Category).where(Category.id == data["category_id"]))).scalar_one_or_none():
                raise ValueError("Категория не найдена")
        if "unit_id" in data:
            if not (await self.session.execute(select(Unit).where(Unit.id == data["unit_id"]))).scalar_one_or_none():
                raise ValueError("Единица измерения не найдена")
        for k, v in data.items():
            setattr(product, k, v)
        await self.session.flush()
        return product

    async def delete(self, product: Product) -> None:
        await self.session.delete(product)
        await self.session.flush()

    # --- Управление ценой ---
    async def set_current_price(self, product_id: int, new_price: float) -> Price:
        # проверить товар
        prod = (await self.session.execute(select(Product).where(Product.id == product_id))).scalar_one_or_none()
        if not prod:
            raise ValueError("Товар не найден")
        # деактивировать текущую
        current = (await self.session.execute(
            select(Price).where(Price.product_id == product_id, Price.is_current.is_(True))
        )).scalar_one_or_none()

        old_price_value = None
        if current:
            current.is_current = False
            current.end_date = datetime.utcnow()
            old_price_value = float(current.price)

        price = Price(
            product_id=product_id,
            price=new_price,
            is_current=True,
            start_date=datetime.utcnow(),
            old_price=old_price_value,
        )
        self.session.add(price)
        await self.session.flush()
        return price
