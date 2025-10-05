"""Хендлер /start: регистрация пользователя по Telegram ID и приветствие."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from app.core.db import get_session
from app.services.user_service import UserService
from app.core.config import settings

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    # Парсим данные Telegram-пользователя
    tg_user = message.from_user
    if tg_user is None:
        await message.answer("Не удалось получить данные пользователя.")
        return

    tg_id = tg_user.id
    full_name = tg_user.full_name
    username = tg_user.username
    first_name = tg_user.first_name
    last_name = tg_user.last_name
    is_bot = tg_user.is_bot
    language_code = getattr(tg_user, "language_code", None)
    is_premium = getattr(tg_user, "is_premium", None)

    # Регистрируем/обновляем пользователя в нашей БД
    async for session in get_session():
        service = UserService(session)
        await service.get_or_create_by_telegram(
            telegram_id=tg_id,
            name=full_name,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_bot=is_bot,
            language_code=language_code,
            is_premium=is_premium,
        )
        break

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть магазин", web_app=WebAppInfo(url=settings.frontend_webapp_url or ""))]
    ])
    await message.answer(
        "👋 Добро пожаловать в овощной магазин!\n"
        "Откройте Мини приложение",
    )
