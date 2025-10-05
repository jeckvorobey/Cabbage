from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.schemas.cart import CartItemIn, CartOut
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.schemas.order import OrderCreate, OrderItemIn

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=CartOut)
async def get_cart(user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)):
    svc = CartService(session)
    return await svc.get_cart(user.id)


@router.post("/items", status_code=201)
async def add_item(item: CartItemIn, user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)):
    svc = CartService(session)
    await svc.add_item(user.id, item.product_id, item.quantity)
    return {"ok": True}


@router.patch("/items/{product_id}")
async def update_item(product_id: int, body: CartItemIn, user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)):
    svc = CartService(session)
    await svc.update_item(user.id, product_id, body.quantity)
    return {"ok": True}


@router.delete("/items/{product_id}", status_code=204)
async def remove_item(product_id: int, user=Depends(get_current_user), session: AsyncSession = Depends(get_db_session)):
    svc = CartService(session)
    await svc.remove_item(user.id, product_id)


@router.post("/checkout")
async def checkout(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    delivery_type: str = "delivery",
    address_id: int | None = None,
    payment_method: str | None = None,
):
    cart = CartService(session)
    detailed = (await cart.get_cart(user.id)).items
    if not detailed:
        raise HTTPException(status_code=400, detail="Корзина пуста")

    items = [OrderItemIn(product_id=it.product_id, quantity=int(it.quantity)) for it in detailed]
    data = OrderCreate(
        items=items,
        delivery_type=delivery_type,
        address_id=address_id,
        payment_method=payment_method,
    )

    orders = OrderService(session)
    order = await orders.create_order(user=user, data=data)

    await cart.clear(user.id)
    return order
