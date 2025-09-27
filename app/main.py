"""Точка входа FastAPI.

Собирает приложение, подключает роутеры и готово к запуску через uvicorn.
"""
from __future__ import annotations

from fastapi import FastAPI

from app.api.routers import health as health_router
from app.api.routers import orders as orders_router
from app.api.routers import products as products_router
from app.api.routers import payments as payments_router

app = FastAPI(title="Овощной магазин", version="0.1.0")

# Подключение роутеров
app.include_router(health_router.router)
app.include_router(products_router.router)
app.include_router(orders_router.router)
app.include_router(payments_router.router)


@app.get("/")
async def root() -> dict[str, str]:
    """Корневой эндпоинт: краткая справка."""
    return {"app": "cabbage", "status": "ok"}
