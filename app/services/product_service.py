"""Сервис каталога товаров и изображений."""
from __future__ import annotations

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.product_repository import ProductRepository
from app.repositories.product_image_repository import ProductImageRepository
from app.services.file_service import FileService
from app.schemas.product import ProductOut, ProductImageOut


class ProductService:
    """Бизнес‑логика каталога."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.products = ProductRepository(session)
        self.images = ProductImageRepository(session)
        self.files = FileService()

    async def list_products(self) -> list[ProductOut]:
        """Список товаров с актуальными ценами, единицами и главным изображением."""
        rows = await self.products.list_with_price()
        for r in rows:
            if r.get("primary_image"):
                r["primary_image"] = self.files.url(r.get("primary_image"))
        return [ProductOut(**r) for r in rows]

    async def upload_product_image(self, product_id: int, file: UploadFile, is_primary: bool = False) -> ProductImageOut:
        """Загрузить изображение для продукта (локально)."""
        file_path = await self.files.save_product_image(product_id, file)
        img = await self.images.create(product_id, file_path, is_primary)
        await self.session.commit()
        return ProductImageOut.model_validate(img)

    async def delete_product_image(self, image_id: int) -> None:
        """Удалить изображение продукта (файл и запись)."""
        img = await self.images.get(image_id)
        if not img:
            raise ValueError("Изображение не найдено")
        self.files.delete(img.file_path)
        await self.images.delete(img)
        await self.session.commit()

    async def set_primary_image(self, image_id: int) -> ProductImageOut:
        """Сделать изображение главным."""
        img = await self.images.set_primary(image_id)
        await self.session.commit()
        return ProductImageOut.model_validate(img)

    async def list_product_images(self, product_id: int) -> list[ProductImageOut]:
        """Получить полный список изображений продукта с абсолютными URL."""
        imgs = await self.images.list_for_product(product_id)
        out: list[ProductImageOut] = []
        for i in imgs:
            dto = ProductImageOut.model_validate(i)
            dto.file_path = self.files.url(dto.file_path)  # type: ignore[assignment]
            out.append(dto)
        return out
