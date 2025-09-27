"""Роуты для оформления заказов."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.schemas.order import OrderCreate, OrderOut
from app.schemas.user import UserMe
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=201)
async def create_order(
    data: OrderCreate,
    user: UserMe = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> OrderOut:
    """Создать заказ от имени текущего пользователя.

    Требуется заголовок X-Telegram-Id.
    """
    service = OrderService(session)
    try:
        return await service.create_order(user=user, data=data)  # type: ignore[arg-type]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
