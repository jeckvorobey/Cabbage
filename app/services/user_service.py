"""Сервис работы с пользователями и их адресами."""
from __future__ import annotations

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Address, User
from app.repositories.user_repository import UserRepository
from app.schemas.address import AddressCreate, AddressOut, AddressUpdate


class UserService:
    """Бизнес‑логика, связанная с пользователями и управлением адресами."""

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

    # ===== Адреса пользователя =====

    async def list_addresses(self, *, user_id: int) -> list[AddressOut]:
        res = await self.session.execute(select(Address).where(Address.user_id == user_id).order_by(Address.id))
        rows = res.scalars().all()
        return [AddressOut.model_validate(row) for row in rows]

    async def _unset_default_for_user(self, user_id: int) -> None:
        await self.session.execute(
            update(Address).where(Address.user_id == user_id, Address.is_default.is_(True)).values(is_default=False)
        )

    async def create_address(self, *, user_id: int, data: AddressCreate) -> AddressOut:
        if data.is_default:
            await self._unset_default_for_user(user_id)
        addr = Address(user_id=user_id, address_line=data.address_line, comment=data.comment, is_default=data.is_default)
        self.session.add(addr)
        await self.session.flush()
        await self.session.commit()
        return AddressOut.model_validate(addr)

    async def update_address(self, *, user_id: int, address_id: int, data: AddressUpdate) -> AddressOut:
        res = await self.session.execute(select(Address).where(Address.id == address_id, Address.user_id == user_id))
        addr = res.scalar_one_or_none()
        if not addr:
            raise ValueError("Адрес не найден")
        if data.is_default is True:
            await self._unset_default_for_user(user_id)
        if data.address_line is not None:
            addr.address_line = data.address_line
        if data.comment is not None:
            addr.comment = data.comment
        if data.is_default is not None:
            addr.is_default = data.is_default
        await self.session.flush()
        await self.session.commit()
        return AddressOut.model_validate(addr)

    async def delete_address(self, *, user_id: int, address_id: int) -> None:
        await self.session.execute(
            delete(Address).where(Address.id == address_id, Address.user_id == user_id)
        )
        await self.session.commit()
