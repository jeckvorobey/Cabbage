"""Роуты управления адресами пользователя."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.models.user import Address
from app.schemas.address import AddressCreate, AddressOut, AddressUpdate
from app.schemas.user import UserMe
from app.services.user_service import UserService

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.get("", response_model=list[AddressOut])
async def list_addresses(
    user: UserMe = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[AddressOut]:
    svc = UserService(session)
    return await svc.list_addresses(user_id=user.id)


@router.post("", response_model=AddressOut, status_code=status.HTTP_201_CREATED)
async def create_address(
    payload: AddressCreate,
    user: UserMe = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> AddressOut:
    svc = UserService(session)
    return await svc.create_address(user_id=user.id, data=payload)


@router.patch("/{address_id}", response_model=AddressOut)
async def update_address(
    address_id: int,
    payload: AddressUpdate,
    user: UserMe = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> AddressOut:
    # Проверим принадлежность адреса пользователю
    res = await session.execute(select(Address).where(Address.id == address_id, Address.user_id == user.id))
    if not res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Адрес не найден")

    svc = UserService(session)
    return await svc.update_address(user_id=user.id, address_id=address_id, data=payload)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: int,
    user: UserMe = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    # Проверим принадлежность адреса пользователю
    res = await session.execute(select(Address).where(Address.id == address_id, Address.user_id == user.id))
    if not res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Адрес не найден")

    svc = UserService(session)
    await svc.delete_address(user_id=user.id, address_id=address_id)
