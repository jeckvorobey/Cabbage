"""Сервис для локального хранения изображений продуктов."""
from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile, HTTPException

from app.core.config import settings


class FileService:
    """Управление загрузкой, удалением и URL для локальных медиа-файлов."""

    def __init__(self) -> None:
        self.root = Path(settings.media_root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _dir_for_product(self, product_id: int) -> Path:
        p = self.root / "products" / str(product_id)
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _gen_name(self, original: str) -> str:
        ext = Path(original).suffix.lower()
        if ext not in settings.allowed_image_extensions:
            raise HTTPException(400, f"Недопустимый формат файла: {ext}")
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{ts}_{uuid.uuid4().hex[:8]}{ext}"

    async def save_product_image(self, product_id: int, file: UploadFile) -> str:
        # Проверка размера
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        if size > settings.max_upload_size_mb * 1024 * 1024:
            raise HTTPException(400, f"Файл слишком большой (>{settings.max_upload_size_mb}MB)")

        target_dir = self._dir_for_product(product_id)
        name = self._gen_name(file.filename or "image.jpg")
        path = target_dir / name
        content = await file.read()
        path.write_bytes(content)
        return f"products/{product_id}/{name}"

    def delete(self, file_path: str) -> None:
        p = self.root / file_path
        if p.exists():
            p.unlink()

    def url(self, file_path: str | None) -> str | None:
        if not file_path:
            return None
        return f"{settings.media_url_prefix}/{file_path}"
