from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role_at_most, get_db_session
from app.models.user import UserRole
from app.models.catalog import Product
from app.schemas.product import ProductIn, ProductUpdate
from app.repositories.product_repository import ProductRepository

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", status_code=201, dependencies=[Depends(require_role_at_most(UserRole.MANAGER))])
async def create_product(data: ProductIn, session: AsyncSession = Depends(get_db_session)):
    repo = ProductRepository(session)
    p = await repo.create(data.model_dump())
    await session.commit()
    return {"id": p.id}


@router.put("/{product_id}", dependencies=[Depends(require_role_at_most(UserRole.MANAGER))])
async def update_product(product_id: int, data: ProductUpdate, session: AsyncSession = Depends(get_db_session)):
    p = await session.get(Product, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Товар не найден")
    repo = ProductRepository(session)
    await repo.update(p, data.model_dump(exclude_none=True))
    await session.commit()
    return {"ok": True}


@router.delete("/{product_id}", status_code=204, dependencies=[Depends(require_role_at_most(UserRole.ADMIN))])
async def delete_product(product_id: int, session: AsyncSession = Depends(get_db_session)):
    p = await session.get(Product, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Товар не найден")
    await session.delete(p)
    await session.commit()


class PriceIn(BaseModel):
    price: float


@router.post("/{product_id}/price", dependencies=[Depends(require_role_at_most(UserRole.MANAGER))])
async def set_price(product_id: int, body: PriceIn, session: AsyncSession = Depends(get_db_session)):
    repo = ProductRepository(session)
    await repo.set_current_price(product_id, body.price)
    await session.commit()
    return {"ok": True}
