from app.delivery_settings.endpoint import delivery
from fastapi import APIRouter


delivery_router = APIRouter()


delivery_router.include_router(delivery.router, prefix="/delivery", tags=["delivery"])
