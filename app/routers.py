from fastapi import APIRouter
from app.catalog.route import catalog_router
from app.users.route import user_router
from app.delivery_settings.route import delivery_router
from app.orders.route import order_router

api_router = APIRouter()

api_router.include_router(catalog_router)
api_router.include_router(user_router)
api_router.include_router(delivery_router)
api_router.include_router(order_router)
