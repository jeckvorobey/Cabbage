"""Репозиторий для работы с изображениями продуктов."""
from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import ProductImage
from .base import BaseRepository


class ProductImageRepository(BaseRepository):
    """CRUD операции и управление главным изображением."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(self, product_id: int, file_path: str, is_primary: bool = False, sort_order: int = 0) -> ProductImage:
        if is_primary:
            await self.session.execute(
                update(ProductImage).where(ProductImage.product_id == product_id).values(is_primary=False)
            )
        img = ProductImage(product_id=product_id, file_path=file_path, is_primary=is_primary, sort_order=sort_order)
        self.session.add(img)
        await self.session.flush()
        return img

    async def get(self, image_id: int) -> ProductImage | None:
        res = await self.session.execute(select(ProductImage).where(ProductImage.id == image_id))
        return res.scalar_one_or_none()

    async def list_for_product(self, product_id: int) -> list[ProductImage]:
        res = await self.session.execute(
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.is_primary.desc(), ProductImage.sort_order, ProductImage.id)
        )
        return list(res.scalars().all())

    async def set_primary(self, image_id: int) -> ProductImage:
        img = await self.get(image_id)
        if not img:
            raise ValueError("Изображение не найдено")
        await self.session.execute(
            update(ProductImage).where(ProductImage.product_id == img.product_id).values(is_primary=False)
        )
        img.is_primary = True
        await self.session.flush()
        return img

    async def delete(self, image: ProductImage) -> None:
        await self.session.delete(image)
        await self.session.flush()
