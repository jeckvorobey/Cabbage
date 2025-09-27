"""Запуск Telegram‑бота в режиме polling.

Требует TELEGRAM_BOT_TOKEN в окружении (.env или переменные окружения).
"""
from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher

from app.core.config import settings
from app.telegram.handlers.start import router as start_router


async def main() -> None:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан в окружении")

    bot = Bot(settings.telegram_bot_token)
    dp = Dispatcher()

    # Роуты бота
    dp.include_router(start_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
