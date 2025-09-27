"""Репозиторий товаров и цен."""
from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.catalog import Price, Product, Unit
from .base import BaseRepository


class ProductRepository(BaseRepository):
    """Запросы каталога с актуальными ценами."""

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
                p.stock_quantity,
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