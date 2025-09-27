"""Роуты каталога товаров."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.product import ProductOut
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
async def list_products(session: AsyncSession = Depends(get_db_session)) -> list[ProductOut]:
    """Список всех товаров с актуальной ценой."""
    service = ProductService(session)
    return await service.list_products()
