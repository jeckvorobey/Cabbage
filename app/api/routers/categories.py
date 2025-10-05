from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role_at_most, get_db_session
from app.models.user import UserRole
from app.models.catalog import Category
from app.schemas.category import CategoryIn, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", status_code=201, dependencies=[Depends(require_role_at_most(UserRole.MANAGER))])
async def create_category(data: CategoryIn, session: AsyncSession = Depends(get_db_session)):
    c = Category(**data.model_dump())
    session.add(c)
    await session.commit()
    await session.refresh(c)
    return {"id": c.id}


@router.put("/{category_id}", dependencies=[Depends(require_role_at_most(UserRole.MANAGER))])
async def update_category(category_id: int, data: CategoryUpdate, session: AsyncSession = Depends(get_db_session)):
    c = await session.get(Category, category_id)
    if not c:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(c, k, v)
    await session.commit()
    return {"ok": True}


@router.delete("/{category_id}", status_code=204, dependencies=[Depends(require_role_at_most(UserRole.ADMIN))])
async def delete_category(category_id: int, session: AsyncSession = Depends(get_db_session)):
    c = await session.get(Category, category_id)
    if not c:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    await session.delete(c)
    await session.commit()
