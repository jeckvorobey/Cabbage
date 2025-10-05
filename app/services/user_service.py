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

    async def get_or_create_by_telegram(
        self,
        *,
        telegram_id: int,
        name: str | None = None,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        is_bot: bool | None = None,
        language_code: str | None = None,
        is_premium: bool | None = None,
    ) -> User:
        """Найти пользователя по Telegram ID или создать нового покупателя.

        Если пользователь существует, обновляет его поля новыми значениями (��сли они переданы).
        """
        user = await self.users.get_by_telegram_id(telegram_id)
        if user:
            # Обновление только переданных значений
            if name is not None:
                user.name = name
            if username is not None:
                user.username = username
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if is_bot is not None:
                user.is_bot = is_bot
            if language_code is not None:
                user.language_code = language_code
            if is_premium is not None:
                user.is_premium = is_premium
            await self.session.flush()
            await self.session.commit()
            return user

        user = await self.users.create(
            telegram_id=telegram_id,
            name=name,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_bot=bool(is_bot) if is_bot is not None else False,
            language_code=language_code,
            is_premium=bool(is_premium) if is_premium is not None else False,
        )
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
