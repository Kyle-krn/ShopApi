from attr import attr
from fastapi import APIRouter, HTTPException
from ..models import JsonbSet, Product, Category
from ..schemas import CategoryFilters, GetCategory, CreateCategory, UpdateCategory, Status
from tortoise.contrib.fastapi import HTTPNotFoundError
from typing import List
from tortoise.expressions import F

category_router = APIRouter()


@category_router.get("/main", response_model=List[GetCategory])
async def get_users():
    """Получить список категорий"""
    return await GetCategory.from_queryset(Category.filter(parent_id__isnull=True))


@category_router.post("/create", response_model=GetCategory)
async def category_route(category: CreateCategory):
    """Создать категорию. Нельзя добавлять в родительскую категорию категории которые имеют товары или фильтры к товарам
    """
    if category.parent_id is not None:
        parent_category_products = Product.filter(category_id=category.parent_id)
        if len(await parent_category_products) > 0:
            raise HTTPException(status_code=400, detail=f"Нельзя добавлять подкатегорию в категорию с товарами.")
        if (await Category.get(id=category.parent_id)).filters != {}:
            raise HTTPException(status_code=400, detail=f"Нельзя добавлять подкатегорию в категорию с фильтрами.")

    category_obj = await Category.create(**category.dict())
    return await GetCategory.from_tortoise_orm(category_obj)


@category_router.get("/{category_id}", response_model=GetCategory, responses={404: {"model": HTTPNotFoundError}})
async def get_category(category_id: int):
    """Получить категорию по id"""
    return await GetCategory.from_tortoise_orm(await Category.get(id=category_id))


@category_router.patch("/{category_id}", response_model=GetCategory, responses={404: {"model": HTTPNotFoundError}})
async def patch_category(category_id: int, category: UpdateCategory):
    """Изменить категорию. Нельзя добавлять в родительскую категорию категории которые имеют товары или фильтры к товарам,
       Фильтры для категорий предназначены для фильтрации товара в каталоге, если по этому эндпоинту передать filters, то у всех товаров в этой категории 
       полностью перепишутся атрибуты.
    """
    
    category_obj = await Category.get(id=category_id)
    if category.parent_id:
        parent_category_products = Product.filter(category_id=category.parent_id)
        if len(await parent_category_products) > 0:
            raise HTTPException(status_code=400, detail=f"Нельзя добавлять подкатегорию в категорию с товарами.")

    if category.filters and category.filters != []:
        if len(await category_obj.children.all()) > 0:
            raise HTTPException(status_code=400, detail=f"Нельзя добавлять фильтры в категорию с подкатегориями.")
        attr_for_product = [{"name":i.name, "value":i.value} for i in category.filters]
        await Product.filter(category=category_obj).update(attributes=attr_for_product)
    elif category.filters == []:
        await Product.filter(category=category_obj).update(attributes=[])
    elif category.filters is None:
        del category.filters
        
    await category_obj.update_from_dict(category.dict())
    await category_obj.save()
    return await GetCategory.from_tortoise_orm(category_obj)



@category_router.patch("/add_attr/{category_id}", response_model=GetCategory, responses={404: {"model": HTTPNotFoundError}})
async def add_attr_in_category(category_id, category_attr: List[CategoryFilters]):
    print(category_attr)
    pass

@category_router.delete("/{category_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_user(category_id: int):
    deleted_count = await Category.filter(id=category_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {category_id} not found")
    return Status(message=f"Deleted category {category_id}")


