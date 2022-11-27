from fastapi import APIRouter

# from app.catalog.endpoint import category, product
from app.orders.endpoint import telegram_orders

order_router = APIRouter()


order_router.include_router(telegram_orders.telegram_order_router, prefix="/orders", tags=["orders"])
# order_router.include_router(product.product_router, prefix="/product", tags=["product"])
