"""Сервис работы с пользователями."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    """Бизнес‑логика, связанная с пользователями."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def get_or_create_by_telegram(self, telegram_id: int, name: str | None = None) -> User:
        """Найти пользователя по Telegram ID или создать нового покупателя."""
        user = await self.users.get_by_telegram_id(telegram_id)
        if user:
            return user
        user = await self.users.create(telegram_id=telegram_id, name=name)
        await self.session.commit()
        return user
