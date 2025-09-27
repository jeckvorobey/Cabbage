"""Репозиторий пользователей."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from .base import BaseRepository


class UserRepository(BaseRepository):
    """CRUD и спец‑запросы к пользователям."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create(self, telegram_id: int, name: str | None = None) -> User:
        user = User(telegram_id=telegram_id, name=name)
        self.session.add(user)
        await self.session.flush()
        return user
