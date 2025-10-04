"""Сервис заказов: создание заказов, базовые операции.
Более сложные сценарии (FSM, смена статусов менеджером) предполагаются на следующих этапах.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Address, User
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderItemOut, OrderOut


class OrderService:
    """Бизнес‑логика заказов."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.orders = OrderRepository(session)

    async def create_order(self, *, user: User, data: OrderCreate) -> OrderOut:
        """Создать заказ от имени пользователя и вернуть DTO."""
        # Валидация адреса в зависимости от типа доставки
        if data.delivery_type == "delivery":
            if not data.address_id:
                raise ValueError("Для доставки требуется address_id")
            res = await self.session.execute(
                select(Address).where(Address.id == data.address_id, Address.user_id == user.id)
            )
            if not res.scalar_one_or_none():
                raise ValueError("Адрес не найден или не принадлежит пользователю")
        elif data.delivery_type == "pickup":
            # Для самовывоза address_id не требуется
            pass
        else:
            raise ValueError("Недопустимый тип доставки: ожидается 'delivery' или 'pickup'")

        pairs = [(item.product_id, item.quantity) for item in data.items]
        order = await self.orders.create_order(
            user_id=user.id,
            items=pairs,
            delivery_type=data.delivery_type,
            address_id=data.address_id,
            payment_method=data.payment_method,
        )
        await self.session.commit()

        items = [
            OrderItemOut(product_id=it.product_id, quantity=float(it.quantity), price=float(it.price))
            for it in order.items
        ]
        return OrderOut(
            id=order.id,
            order_date=order.order_date,
            status=order.status,  # type: ignore[arg-type]
            is_paid=order.is_paid,
            delivery_type=order.delivery_type,
            address_id=order.address_id,
            total_amount=float(order.total_amount) if order.total_amount is not None else None,
            items=items,
        )
