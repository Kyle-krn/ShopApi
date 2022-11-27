# from http.client import HTTPException
from fastapi import APIRouter
from tortoise import List
from app.catalog.models import Product
from app.orders.models import TelegramOrder, SaleProduct
from app.orders.schemas import CreateTelegramOrder, CreatePPOrder, GetPPOrder, GetOrder
from app.catalog.schemas import Status
from fastapi import APIRouter, Depends, HTTPException
from app.users.models import UserDB
from app.users.route import current_active_user, current_superuser

import random

telegram_order_router = APIRouter()


@telegram_order_router.get(path="/get-order-by-tg-id/{tg_id}", response_model=List[GetOrder])
async def get_user_order(tg_id: int, user: UserDB = Depends(current_active_user)):
    """Получить заказ по telegram_id"""
    return await GetOrder.from_queryset(TelegramOrder.filter(tg_id=tg_id))


@telegram_order_router.get(path="/get-order/{order_id}", response_model=GetOrder)
async def get_order(order_id: int, user: UserDB = Depends(current_active_user)):
    """Получить заказ по id"""
    return await GetOrder.from_tortoise_orm(await TelegramOrder.get(id=order_id))


@telegram_order_router.post(path="/create-shipping-order", response_model=Status)
async def create_shipping_order(data: CreateTelegramOrder):
    order_products = data.products
    del data.products
    if order_products == []:
        raise HTTPException(status_code=400, detail=f"Список товаров пуст.")
    order = await TelegramOrder.create(**data.dict())
    for item in order_products:
        product = await Product.get(id=item.id)
        product.quantity -= item.quantity
        await product.save()
        await SaleProduct.create(
            product=product,
            price=product.price,
            discount=product.discount,
            name=product.name,
            quantity=item.quantity,
            order=order,
        )
    return Status(message=f"Заказ #{order.id} успешно создан!")


@telegram_order_router.post(path="/create-pp-order", response_model=GetPPOrder)
async def create_pp_order(data: CreatePPOrder, user: UserDB = Depends(current_active_user)):
    order_products = data.products
    del data.products
    if order_products == []:
        raise HTTPException(status_code=400, detail=f"Список товаров пуст.")
    order = await TelegramOrder.create(**data.dict())
    order.pickup_code = random.randint(1000, 9999)
    await order.save()
    for item in order_products:
        product = await Product.get(id=item.id)
        product.quantity -= item.quantity
        await product.save()
        await SaleProduct.create(
            product=product,
            price=product.price,
            discount=product.discount,
            name=product.name,
            quantity=item.quantity,
            order=order,
        )
    return GetPPOrder(message=f"Заказ #{order.id} успешно создан!", code=order.pickup_code)
