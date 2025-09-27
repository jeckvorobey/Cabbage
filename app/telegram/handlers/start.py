"""Хендлер /start: регистрация пользователя по Telegram ID и приветствие."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.core.db import get_session
from app.services.user_service import UserService

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    # Регистрируем пользователя в нашей БД (если его ещё нет)
    tg_id = message.from_user.id if message.from_user else None
    full_name = message.from_user.full_name if message.from_user else None
    if tg_id is not None:
        async for session in get_session():
            service = UserService(session)
            await service.get_or_create_by_telegram(telegram_id=tg_id, name=full_name)
            break

    await message.answer(
        "👋 Добро пожаловать в овощной магазин!\n"
        "Откройте WebApp или пользуйтесь командами бота."
    )
