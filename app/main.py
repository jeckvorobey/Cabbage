"""Точка входа FastAPI.

Собирает приложение, подключает роутеры и запускает Telegram‑бота
в режиме polling (dev) или webhook (prod) в зависимости от настроек окружения.
"""
from __future__ import annotations

import asyncio
import contextlib

from fastapi import FastAPI, Header, HTTPException, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from app.api.routers import health as health_router
from app.api.routers import orders as orders_router
from app.api.routers import products as products_router
from app.api.routers import payments as payments_router
from app.core.config import settings
from app.telegram.handlers.start import router as start_router

app = FastAPI(title="Овощной магазин", version="0.1.0")

# Подключение REST-роутеров
app.include_router(health_router.router)
app.include_router(products_router.router)
app.include_router(orders_router.router)
app.include_router(payments_router.router)


@app.get("/")
async def root() -> dict[str, str]:
    """Корневой эндпоинт: краткая справка."""
    return {"app": "cabbage", "status": "ok"}


# ===== Telegram Bot (aiogram v3) =====
bot: Bot | None = None
dp: Dispatcher | None = None


@app.on_event("startup")
async def on_startup() -> None:
    """Инициализация Telegram‑бота.

    - В режиме webhook: регистрирует вебхук в Telegram.
    - В режиме polling: удаляет вебхук и запускает polling в фоне.
    """
    global bot, dp

    if not settings.telegram_bot_token:
        # Токен не задан — пропускаем инициализацию бота
        return

    bot = Bot(settings.telegram_bot_token, parse_mode="HTML")
    dp = Dispatcher()
    # Подключаем роутеры бота
    dp.include_router(start_router)

    if settings.telegram_mode == "webhook":
        if not settings.telegram_webhook_url:
            raise RuntimeError("TELEGRAM_WEBHOOK_HOST/TELEGRAM_WEBHOOK_PATH не настроены для webhook режима")
        await bot.set_webhook(
            settings.telegram_webhook_url,
            secret_token=settings.telegram_webhook_secret,
            drop_pending_updates=True,
        )
    else:
        # Убедимся, что вебхук снят, и стартуем polling в фоновом таске
        await bot.delete_webhook(drop_pending_updates=True)
        app.state.bot_task = asyncio.create_task(
            dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types() if dp else None,
            )
        )


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Корректное завершение фоновых задач и закрытие сессии бота."""
    task = getattr(app.state, "bot_task", None)
    if task:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

    if bot:
        await bot.session.close()


@app.post(settings.telegram_webhook_path)
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(None),
) -> dict[str, bool]:
    """Обработчик обновлений Telegram в режиме webhook.

    Требуется активный режим webhook и, при задании секрета, корректный заголовок
    X-Telegram-Bot-Api-Secret-Token.
    """
    if settings.telegram_mode != "webhook":
        return {"ok": True}

    if settings.telegram_webhook_secret and x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
        raise HTTPException(status_code=403, detail="invalid secret")

    if not (bot and dp):
        raise HTTPException(status_code=503, detail="bot is not initialized")

    payload = await request.json()
    update = Update.model_validate(payload)
    await dp.feed_webhook_update(bot, update)
    return {"ok": True}
