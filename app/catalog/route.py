from fastapi import APIRouter
from app.catalog.endpoint import category, product

catalog_router = APIRouter()


catalog_router.include_router(category.category_router, prefix="/category", tags=["category"])
catalog_router.include_router(product.product_router, prefix="/product", tags=["product"])
