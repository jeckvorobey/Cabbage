from __future__ import annotations

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.cart_repository import CartRepository
from app.schemas.cart import CartOut, CartItemOut


class CartService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = CartRepository(session)

    async def get_cart(self, user_id: int) -> CartOut:
        rows = await self.repo.fetch_detailed(user_id)
        total = Decimal("0.00")
        for r in rows:
            if r["line_total"] is not None:
                total += Decimal(str(r["line_total"]))
        return CartOut(
            items=[CartItemOut(**r) for r in rows],
            total=float(total)
        )

    async def add_item(self, user_id: int, product_id: int, qty: int) -> None:
        if qty <= 0:
            raise ValueError("Количество должно быть > 0")
        await self.repo.add_item(user_id, product_id, qty)
        await self.session.commit()

    async def update_item(self, user_id: int, product_id: int, qty: int) -> None:
        await self.repo.update_item(user_id, product_id, qty)
        await self.session.commit()

    async def remove_item(self, user_id: int, product_id: int) -> None:
        await self.repo.remove_item(user_id, product_id)
        await self.session.commit()

    async def clear(self, user_id: int) -> None:
        await self.repo.clear(user_id)
        await self.session.commit()
