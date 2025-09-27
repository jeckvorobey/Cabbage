"""Зависимости FastAPI: получение сессии БД и текущего пользователя по Telegram ID."""
from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.schemas.user import UserMe
from app.services.user_service import UserService


async def get_db_session() -> AsyncSession:
    """Асинхронная сессия БД."""
    async for s in get_session():
        return s
    raise RuntimeError("Не удалось получить сессию БД")


async def get_current_user(
    x_telegram_id: int | None = Header(default=None, alias="X-Telegram-Id"),
    session: AsyncSession = Depends(get_db_session),
) -> UserMe:
    """Получить (или создать) пользователя по заголовку X-Telegram-Id.

    Для прототипа имя не требуется — при первом обращении создаём пользователя‑покупателя.
    """
    if x_telegram_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Требуется X-Telegram-Id")

    user_service = UserService(session)
    user = await user_service.get_or_create_by_telegram(telegram_id=x_telegram_id)
    return UserMe(id=user.id, telegram_id=user.telegram_id, role=user.role)  # type: ignore[arg-type]
