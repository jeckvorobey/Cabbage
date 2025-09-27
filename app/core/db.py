"""Инициализация асинхронного подключения к БД и декларативной базы моделей."""
from __future__ import annotations

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    """База для всех ORM‑моделей."""


engine: AsyncEngine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Зависимость FastAPI: выдаёт асинхронную сессию БД и закрывает её по завершению запроса."""
    async with SessionLocal() as session:
        yield session
