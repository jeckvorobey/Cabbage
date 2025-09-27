"""Сервис каталога товаров."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductOut


class ProductService:
    """Бизнес‑логика каталога."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.products = ProductRepository(session)

    async def list_products(self) -> list[ProductOut]:
        """Список товаров с актуальными ценами и единицами."""
        rows = await self.products.list_with_price()
        return [ProductOut(**row) for row in rows]
