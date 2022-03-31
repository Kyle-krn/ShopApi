from math import prod
from fastapi import APIRouter, HTTPException
from ..models import Product, Category, JsonbSet
from ..schemas import GetProduct, CreateProduct, validate_json_attr, Status
from tortoise.contrib.fastapi import HTTPNotFoundError
from typing import List, Any
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel
from .. import schemas, service, models
from tortoise.expressions import F
from pypika.terms import Function

product_router = APIRouter()


@product_router.post("/create", response_model=GetProduct)
async def create_product(product: CreateProduct):
    category = await Category.get(id = product.category_id)
    children = category.children
    if len(await children) != 0:
        raise HTTPException(status_code=400, detail=f"Нельзя добавлять товар в категорию с подкатегориями.")
    try:
        validate_json_attr(category.filters, product.attributes)
    except (IndexError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    product_obj = await Product.create(**product.dict())
    return await GetProduct.from_tortoise_orm(product_obj)


@product_router.delete("/delete_all", response_model=Status)
async def delete_all_product():
    await Product.all().delete()
    return Status(message="Все товары удалены")


@product_router.get("/all", response_model=List[GetProduct])
async def get_all_product():
    return await GetProduct.from_queryset(Product.all())


@product_router.delete("/{product_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_all_product(product_id):
    deleted_count = await Product.get(id=product_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Товар #{product_id} не найден.")
    return Status(message=f"Товар {product_id} успешно удален.")


@product_router.get("/by_category/{category_id}", response_model=List[GetProduct], responses={404: {"model": HTTPNotFoundError}})
async def get_product_by_id(category_id):
    return await GetProduct.from_queryset(Product.filter(category_id=category_id))


@product_router.patch("/{product_id}", response_model=GetProduct, responses={404: {"model": HTTPNotFoundError}})
async def update_product(product_id):
    product_obj = await Product.get(id=product_id)


@product_router.get("/{product_id}", response_model=GetProduct, responses={404: {"model": HTTPNotFoundError}})
async def get_product(product_id):
    product_obj = await Product.get(id=product_id)
    product_obj.attributes = {}
    await product_obj.save()
    # sql = Product.filter(pk=product_id).update(attributes=JsonbSet(F("attributes"), "{a}", "3")).sql()
    # print(sql)
    return await GetProduct.from_tortoise_orm(await Product.get(id=product_id))