"""Хендлер /start: регистрация пользователя по Telegram ID и приветствие."""
from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from app.core.db import get_session
from app.services.user_service import UserService
from app.core.config import settings

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    # Парсим данные Telegram-пользователя
    tg_user = message.from_user
    if tg_user is None:
        logger.warning("Получено сообщение /start без данных пользователя")
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

    logger.info(f"Команда /start от пользователя {tg_id} (@{username})")

    # Сохраняем JSON объект пользователя в файл
    try:
        import json
        from pathlib import Path

        dump_dir = Path(__file__).parent.parent / "user_data"
        dump_dir.mkdir(parents=True, exist_ok=True)
        user_json_path = dump_dir / f"{tg_id}.json"

        # aiogram v3: у объекта User есть метод model_dump()
        user_payload = tg_user.model_dump() if hasattr(tg_user, "model_dump") else {
            "id": tg_id,
            "full_name": full_name,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "is_bot": is_bot,
            "language_code": language_code,
            "is_premium": is_premium,
        }
        user_json_path.write_text(json.dumps(user_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.debug(f"Данные пользователя {tg_id} сохранены в {user_json_path}")
    except Exception as e:
        # Не падаем на ошибке записи файла
        logger.error(f"Не удалось сохранить JSON пользователя {tg_id}: {e}", exc_info=True)

    # Регистрируем/обновляем пользователя в нашей БД
    try:
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
            logger.info(f"Пользователь {tg_id} зарегистрирован/обновлён в БД")
            break
    except Exception as e:
        logger.error(f"Ошибка регистрации пользователя {tg_id} в БД: {e}", exc_info=True)
        await message.answer("Произошла ошибка. Попробуйте позже.")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть магазин", web_app=WebAppInfo(url=settings.frontend_webapp_url or ""))]
    ])
    await message.answer(
        "👋 Добро пожаловать в овощной магазин!\n"
        "Откройте Мини приложение",
        reply_markup=kb,
    )
    logger.debug(f"Приветственное сообщение отправлено пользователю {tg_id}")
