"""Запуск Telegram‑бота в режиме polling.

Требует TELEGRAM_BOT_TOKEN в окружении (.env или переменные окружения).
"""
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

# Настройка логирования перед импортом settings
from app.core.logging import setup_logging
setup_logging()

from app.core.config import settings
from app.telegram.handlers.start import router as start_router

logger = logging.getLogger(__name__)


async def main() -> None:
    """Асинхронно запускает Telegram-бота.

    Инициализирует бота с токеном из настроек, настраивает диспетчер,
    подключает роутер start_router и начинает опрос обновлений (polling).
    Если TELEGRAM_BOT_TOKEN не задан в окружении, выбрасывает RuntimeError.

    Исключения:
        RuntimeError: Если TELEGRAM_BOT_TOKEN не задан в окружении.
    """
    if not settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN не задан в окружении")
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан в окружении")

    logger.info("Инициализация бота...")
    bot = Bot(
        settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()

    # Роуты бота
    dp.include_router(start_router)
    logger.info("Роутеры подключены")

    logger.info("Запуск polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
