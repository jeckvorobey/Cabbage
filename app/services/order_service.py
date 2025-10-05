"""Сервис заказов: создание заказов, базовые операции.
Более сложные сценарии (FSM, смена статусов менеджером) предполагаются на следующих этапах.
"""
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Address, User
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderItemOut, OrderOut

logger = logging.getLogger(__name__)


class OrderService:
    """Бизнес‑логика заказов."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.orders = OrderRepository(session)

    async def create_order(self, *, user: User, data: OrderCreate) -> OrderOut:
        """Создать заказ от имени пользователя и вернуть DTO."""
        logger.info(f"Создание заказа для пользователя {user.id}")
        
        # Валидация адреса в зависимости от типа доставки
        if data.delivery_type == "delivery":
            if not data.address_id:
                logger.warning(f"Попытка создать заказ без адреса: user_id={user.id}")
                raise ValueError("Для доставки требуется address_id")
            res = await self.session.execute(
                select(Address).where(Address.id == data.address_id, Address.user_id == user.id)
            )
            if not res.scalar_one_or_none():
                logger.warning(f"Адрес {data.address_id} не найден или не принадлежит пользователю {user.id}")
                raise ValueError("Адрес не найден или не принадлежит пользователю")
        elif data.delivery_type == "pickup":
            # Для самовывоза address_id не требуется
            logger.debug(f"Заказ с самовывозом для пользователя {user.id}")
        else:
            logger.warning(f"Недопустимый тип доставки: {data.delivery_type}")
            raise ValueError("Недопустимый тип доставки: ожидается 'delivery' или 'pickup'")

        try:
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
            
            logger.info(f"Заказ {order.id} успешно создан для пользователя {user.id}, сумма: {order.total_amount}")
            
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
        except Exception as e:
            logger.error(f"Ошибка создания заказа для user_id={user.id}: {e}", exc_info=True)
            raise
