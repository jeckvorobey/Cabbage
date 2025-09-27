"""Интеграция ЮKassa (заготовка).

На данном этапе реализована простая обёртка с методом создания платежа.
В реальном окружении необходимо задать YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY
и настроить webhook в кабинете ЮKassa на адрес /payments/yookassa/callback.
"""
from __future__ import annotations

from typing import Any

from app.core.config import settings

try:
    from yookassa import Configuration, Payment
except Exception:  # pragma: no cover - если пакет недоступен в окружении тестов
    Configuration = None  # type: ignore[assignment]
    Payment = None  # type: ignore[assignment]


class YooKassaService:
    """Сервис работы с ЮKassa."""

    def __init__(self) -> None:
        self.shop_id = settings.yookassa.shop_id
        self.secret_key = settings.yookassa.secret_key
        if Configuration and self.shop_id and self.secret_key:
            Configuration.account_id = self.shop_id
            Configuration.secret_key = self.secret_key

    async def create_payment(self, *, amount: float, description: str, return_url: str | None = None) -> dict[str, Any]:
        """Создать платёж и вернуть данные подтверждения.

        Возвращает структуру с полем confirmation_url. При отсутствии конфигурации — заглушку.
        """
        if Payment and self.shop_id and self.secret_key:
            # Здесь мог бы быть реальный вызов SDK (синхронный), обёрнутый в executor
            # Но для простоты текущего этапа вернём заглушку
            pass
        return {
            "id": "mock_payment_id",
            "amount": amount,
            "confirmation_url": return_url or settings.yookassa.return_url or "http://localhost/mock/return",
            "description": description,
        }
