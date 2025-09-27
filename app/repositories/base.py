"""Базовый репозиторий: общие помощники для работы с AsyncSession.
Не содержит бизнес‑логики.
"""
from __future__ import annotations

from typing import Any, Iterable

from sqlalchemy import Select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute


class BaseRepository:
    """Базовый класс репозитория.

    Предоставляет минимальный набор утилит для дочерних репозиториев.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def delete_where(self, model: type, where: Iterable[InstrumentedAttribute[Any]]) -> None:
        """Удалить записи по условиям (вспомогательный метод)."""
        stmt = delete(model).where(*where)
        await self.session.execute(stmt)

    async def scalar(self, stmt: Select[Any]) -> Any:
        """Получить один скаляр из select."""
        res = await self.session.execute(stmt)
        return res.scalar()

    async def scalars(self, stmt: Select[Any]) -> list[Any]:
        """Получить список скаляров из select."""
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
