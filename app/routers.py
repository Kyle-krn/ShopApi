from fastapi import APIRouter
from app.catalog.route import catalog_router
from app.users.route import user_router

api_router = APIRouter()

api_router.include_router(catalog_router)
api_router.include_router(user_router)
