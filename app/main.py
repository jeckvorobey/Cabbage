"""Точка входа FastAPI.

Собирает приложение, подключает роутеры и запускает Telegram‑бота
в режиме polling (dev) или webhook (prod) в зависимости от настроек окружения.
"""
from __future__ import annotations

import asyncio
import contextlib
ьштшimport logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.client.default import DefaultBotProperties

# Настройка логирования ПЕРЕД всеми импортами
from app.core.logging import setup_logging
setup_logging()

from app.api.routers import health as health_router
from app.api.routers import orders as orders_router
from app.api.routers import products as products_router
from app.api.routers import payments as payments_router
from app.api.routers import addresses as addresses_router
from app.api.routers import tg_auth as tg_auth_router
from app.core.config import settings
from app.core.middleware import log_requests_middleware
from app.telegram.handlers.start import router as start_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan-хуки вместо on_event.

    - На старте: инициализация бота в режиме webhook или polling.
    - На остановке: остановка фоновой задачи и закрытие сессии бота.
    """
    logger.info("Запуск приложения...")
    bot: Bot | None = None
    dp: Dispatcher | None = None

    if settings.telegram_bot_token:
        logger.info("Инициализация Telegram бота...")
        bot = Bot(
            settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode="HTML")
        )
        dp = Dispatcher()
        dp.include_router(start_router)

        # Делаем бота/диспетчер доступными в обработчиках
        app.state.bot = bot
        app.state.dp = dp

        if settings.telegram_mode == "webhook":
            if not settings.telegram_webhook_url:
                raise RuntimeError(
                    "TELEGRAM_WEBHOOK_HOST/TELEGRAM_WEBHOOK_PATH не настроены для webhook режима"
                )
            logger.info(f"Установка webhook: {settings.telegram_webhook_url}")
            await bot.set_webhook(
                settings.telegram_webhook_url,
                secret_token=settings.telegram_webhook_secret,
                drop_pending_updates=True,
            )
            logger.info("Webhook установлен успешно")
        else:
            # Убедимся, что вебхук снят, и стартуем polling в фоновом таске
            logger.info("Режим polling: удаление webhook...")
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Запуск polling в фоновом режиме...")
            app.state.bot_task = asyncio.create_task(
                dp.start_polling(
                    bot,
                    allowed_updates=dp.resolve_used_update_types(),
                )
            )
            logger.info("Polling запущен")
    else:
        logger.warning("TELEGRAM_BOT_TOKEN не задан, бот не запущен")

    logger.info("Приложение готово к работе")
    
    # Передаём управление приложению
    try:
        yield
    finally:
        # Корректное завершение
        logger.info("Остановка приложения...")
        task = getattr(app.state, "bot_task", None)
        if task:
            logger.info("Остановка polling...")
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

        if bot:
            logger.info("Закрытие сессии бота...")
            await bot.session.close()
        
        logger.info("Приложение остановлено")


app = FastAPI(title="Овощной магазин", version="0.1.0", lifespan=lifespan)

# Middleware для логирования запросов
app.middleware("http")(log_requests_middleware)

# Подключение REST-роутеров
app.include_router(health_router.router)
app.include_router(products_router.router)
app.include_router(orders_router.router)
app.include_router(payments_router.router)
app.include_router(addresses_router.router)
app.include_router(tg_auth_router.router)

logger.info("Роутеры подключены")


@app.get("/")
async def root() -> dict[str, str]:
    """Корневой эндпоинт: краткая справка."""
    return {"app": "cabbage", "status": "ok"}


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
        logger.warning(f"Получен webhook с неверным секретом")
        raise HTTPException(status_code=403, detail="invalid secret")

    bot: Bot | None = getattr(request.app.state, "bot", None)
    dp: Dispatcher | None = getattr(request.app.state, "dp", None)
    if not (bot and dp):
        logger.error("Бот не инициализирован при получении webhook")
        raise HTTPException(status_code=503, detail="bot is not initialized")

    payload = await request.json()
    update = Update.model_validate(payload)
    logger.debug(f"Получен webhook update: {update.update_id}")
    await dp.feed_webhook_update(bot, update)
    return {"ok": True}
