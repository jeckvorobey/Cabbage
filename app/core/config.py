"""Конфигурация приложения через Pydantic Settings.
Все значения читаются из переменных окружения (.env).
"""
from __future__ import annotations

from pydantic import BaseModel
from typing import Literal
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
    telegram_mode: Literal["polling", "webhook"] = "polling"
    telegram_webhook_host: str | None = None  # e.g. https://example.com
    telegram_webhook_path: str = "/telegram/webhook"
    telegram_webhook_secret: str | None = None

    @property
    def telegram_webhook_url(self) -> str | None:
        if self.telegram_webhook_host:
            return f"{self.telegram_webhook_host}{self.telegram_webhook_path}"
        return None

    # YooKassa
    yookassa: YooKassaSettings = YooKassaSettings(
        shop_id=None,
        secret_key=None,
        return_url=None,
        webhook_secret=None,
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__")


settings = Settings()
