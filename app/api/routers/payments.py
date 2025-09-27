"""Роуты платежей (ЮKassa): callback вебхук и (опционально) создание платежа."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.services.payments import YooKassaService

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/yookassa/callback")
async def yookassa_callback(request: Request) -> dict[str, str]:
    """Обработчик webhook от ЮKassa.

    На данном этапе заглушка: принимает JSON и отвечает 200 OK.
    В реальной реализации здесь обновляется статус оплаты заказа.
    """
    try:
        payload: Any = await request.json()
        # TODO: проверить подпись, обновить статус заказа по payload
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"status": "ok"}


@router.post("/yookassa/create")
async def yookassa_create(amount: float, description: str) -> dict[str, Any]:
    """Пример создания платежа (упрощённо)."""
    service = YooKassaService()
    payment = await service.create_payment(amount=amount, description=description)
    return payment
