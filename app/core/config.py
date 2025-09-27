"""Конфигурация приложения через Pydantic Settings.
Все значения читаются из переменных окружения (.env).
"""
from __future__ import annotations

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class YooKassaSettings(BaseModel):
    """Настройки интеграции с ЮKassa."""

    shop_id: str | None = None
    secret_key: str | None = None
    return_url: str | None = None
    webhook_secret: str | None = None


class Settings(BaseSettings):
    """Глобальные настройки приложения."""

    # Общие
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_env: str = "dev"

    # База данных
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cabbage"

    # Telegram
    telegram_bot_token: str | None = None

    # YooKassa
    yookassa: YooKassaSettings = YooKassaSettings(
        shop_id=None,
        secret_key=None,
        return_url=None,
        webhook_secret=None,
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__")


settings = Settings()