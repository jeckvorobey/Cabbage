"""Запуск Telegram‑бота в режиме polling.

Требует TELEGRAM_BOT_TOKEN в окружении (.env или переменные окружения).
"""
from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.core.config import settings
from app.telegram.handlers.start import router as start_router

"""
Асинхронно запускает Telegram-бота.

Инициализирует бота с токеном из настроек, настраивает диспетчер,
подключает роутер start_router и начинает опрос обновлений (polling).
Если TELEGRAM_BOT_TOKEN не задан в окружении, выбрасывает RuntimeError.

Исключения:
    RuntimeError: Если TELEGRAM_BOT_TOKEN не задан в окружении.
"""
async def main() -> None:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан в окружении")

    bot = Bot(
        settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()

    # Роуты бота
    dp.include_router(start_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
