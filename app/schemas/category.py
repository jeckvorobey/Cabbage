from __future__ import annotations

from pydantic import BaseModel


class CategoryIn(BaseModel):
    name: str
    parent_id: int | None = None
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    parent_id: int | None = None
    description: str | None = None
