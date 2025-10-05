from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart, CartItem
from app.models.catalog import Product, Unit
from app.repositories.product_repository import ProductRepository


class CartRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.products = ProductRepository(session)

    async def get_or_create_cart(self, user_id: int) -> Cart:
        res = await self.session.execute(select(Cart).where(Cart.user_id == user_id))
        cart = res.scalar_one_or_none()
        if not cart:
            cart = Cart(user_id=user_id)
            self.session.add(cart)
            await self.session.flush()
        return cart

    async def add_item(self, user_id: int, product_id: int, qty: int) -> None:
        cart = await self.get_or_create_cart(user_id)
        res = await self.session.execute(
            select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
        )
        item = res.scalar_one_or_none()
        if item:
            item.quantity += qty
        else:
            self.session.add(CartItem(cart_id=cart.id, product_id=product_id, quantity=qty))
        await self.session.flush()

    async def update_item(self, user_id: int, product_id: int, qty: int) -> None:
        cart = await self.get_or_create_cart(user_id)
        res = await self.session.execute(
            select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
        )
        item = res.scalar_one_or_none()
        if not item:
            raise ValueError("Товар отсутствует в корзине")
        if qty <= 0:
            await self.session.delete(item)
        else:
            item.quantity = qty
        await self.session.flush()

    async def remove_item(self, user_id: int, product_id: int) -> None:
        cart = await self.get_or_create_cart(user_id)
        res = await self.session.execute(
            select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
        )
        item = res.scalar_one_or_none()
        if item:
            await self.session.delete(item)
            await self.session.flush()

    async def clear(self, user_id: int) -> None:
        cart = await self.get_or_create_cart(user_id)
        res = await self.session.execute(select(CartItem).where(CartItem.cart_id == cart.id))
        for it in res.scalars().all():
            await self.session.delete(it)
        await self.session.flush()

    async def fetch_detailed(self, user_id: int) -> list[dict]:
        cart = await self.get_or_create_cart(user_id)
        res = await self.session.execute(select(CartItem).where(CartItem.cart_id == cart.id))
        items = res.scalars().all()

        detailed = []
        for it in items:
            prod = (await self.session.execute(select(Product).where(Product.id == it.product_id))).scalar_one_or_none()
            if not prod:
                continue
            unit = (await self.session.execute(select(Unit).where(Unit.id == prod.unit_id))).scalar_one_or_none()
            price = await self.products.get_price_for_product(prod.id)
            line_total = (price or 0) * it.quantity if price is not None else None
            detailed.append({
                "product_id": prod.id,
                "quantity": it.quantity,
                "name": prod.name,
                "unit_symbol": unit.symbol if unit else "",
                "price": float(price) if price is not None else None,
                "line_total": float(line_total) if line_total is not None else None,
            })
        return detailed
