"""Репозиторий заказов."""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import Product
from app.models.order import Order, OrderItem
from .base import BaseRepository
from .product_repository import ProductRepository


class OrderRepository(BaseRepository):
    """Создание и управление заказами."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._product_repo = ProductRepository(session)

    async def create_order(
        self,
        *,
        user_id: int,
        items: list[tuple[int, int]],  # (product_id, quantity в граммах)
        delivery_type: str,
        address_id: int | None,
        payment_method: str | None,
    ) -> Order:
        """Создать заказ с позициями и зарезервировать остатки.

        Бросает ValueError, если не хватает остатков или нет актуальной цены.
        Количество трактуется как целое число граммов.
        """
        # Проверки и расчёт суммы
        total = Decimal("0.00")
        product_cache: dict[int, Product] = {}

        for product_id, qty in items:
            # Получаем товар
            prod = product_cache.get(product_id)
            if not prod:
                res = await self.session.execute(select(Product).where(Product.id == product_id))
                prod = res.scalar_one_or_none()
                if not prod:
                    raise ValueError(f"Товар id={product_id} не найден")
                product_cache[product_id] = prod

            # Проверяем остаток (qty в граммах)
            if prod.qty is None or int(prod.qty) < int(qty):
                raise ValueError(f"Недостаточно остатков для товара id={product_id}")

            # Цена за единицу (за 1 товар/упаковку; итог считается как price * qty)
            price = await self._product_repo.get_price_for_product(product_id)
            if price is None:
                raise ValueError(f"Нет актуальной цены для товара id={product_id}")

            total += Decimal(str(price)) * Decimal(str(qty))

        # Создаём заказ
        order = Order(
            user_id=user_id,
            status="created",
            delivery_type=delivery_type,
            address_id=address_id,
            payment_method=payment_method,
            total_amount=float(total),
        )
        self.session.add(order)
        await self.session.flush()

        # Создаём позиции и резервируем товар
        for product_id, qty in items:
            price = await self._product_repo.get_price_for_product(product_id)
            item = OrderItem(order_id=order.id, product_id=product_id, quantity=int(qty), price=price)  # type: ignore[arg-type]
            self.session.add(item)

            # Резервирование — уменьшаем остаток (целые граммы)
            prod = product_cache[product_id]
            prod.qty = int(prod.qty) - int(qty)  # type: ignore[assignment]

        await self.session.flush()
        return order
