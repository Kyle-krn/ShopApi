from sys import prefix
from fastapi import APIRouter, HTTPException
from ..models import Product, Category
from ..schemas import CategoryFilters, ChangeNameAttr, GetCategory, CreateCategory, UpdateCategory, Status, RemoveAttr
from tortoise.contrib.fastapi import HTTPNotFoundError
from typing import List
from utils.utils import generate_string_sql_query
from ..models import rowsql_add_attrs_for_all_category, rowsql_remote_attrs_for_all_category, rowsql_update_attr_name

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
       полностью перепишутся атрибуты, для bool значений передавайте "false" or "true".
    """
    category_obj = await Category.get(id=category_id)
    
    if category.parent_id:
        '''Проверяем если у родительской категории товар'''
        parent_category_products = Product.filter(category_id=category.parent_id)
        if len(await parent_category_products) > 0:
            raise HTTPException(status_code=400, detail=f"Нельзя добавлять подкатегорию в категорию с товарами.")

    if category.filters and category.filters != []:
        
        if len(await category_obj.children.all()) > 0:
            raise HTTPException(status_code=400, detail=f"Нельзя добавлять фильтры в категорию с подкатегориями.")
        attr_for_product = [{"name":i.name, "value":None} for i in category.filters]
        await Product.filter(category=category_obj).update(attributes=attr_for_product)
    elif category.filters == []:
        await Product.filter(category=category_obj).update(attributes=[])
    elif category.filters is None:
        del category.filters
        
    await category_obj.update_from_dict(category.dict())
    await category_obj.save()
    return await GetCategory.from_tortoise_orm(category_obj)


# SET attributes = attributes || '{"name": "newattr", "value": true}'


@category_router.patch("/add_attr/{category_id}", response_model=GetCategory, responses={404: {"model": HTTPNotFoundError}})
async def add_attr_in_category(category_id, category_attrs: List[CategoryFilters]):
    '''Добавляет атрибуты в фильтры категории и автоматически добавляет атрибут ко всем товарам в категории со значением None'''
    category = await Category.get(id=category_id)
    category_attrs_for_sql = []
    for attr in category_attrs:
        result = list(filter(lambda x: (x["name"] == attr.name), category.filters)) if category.filters else None
        if not result:
            '''Если в body передается атрибут который уже есть в фильтрах категории, он просто пропускается'''
            category_attrs_for_sql.append(attr)
    string_sql_for_category, string_sql_for_product  = await generate_string_sql_query(category_attrs_for_sql)
    if string_sql_for_category:
        await rowsql_add_attrs_for_all_category(string_sql_for_category, string_sql_for_product, category_id)
    
    return await GetCategory.from_tortoise_orm(await Category.get(id=category_id))


@category_router.patch("/change_attr/{category_id}", response_model=GetCategory, responses={404: {"model": HTTPNotFoundError}})
async def change_attr(category_id, data_attr: List[ChangeNameAttr]):
    '''Изменяет имя или префикс фильтра и атрибутов'''
    category = await Category.get(id=category_id)
    category_attrs_for_sql = []
    for attr in data_attr:
        result = list(filter(lambda x: (x["name"] == attr.old_name), category.filters)) if category.filters else None
        if result:
            '''Если в body передается атрибут который уже есть в фильтрах категории, он просто пропускается'''
            category_attrs_for_sql.append(attr)
    for attr in category_attrs_for_sql:
        await rowsql_update_attr_name(old_name=attr.old_name, new_name=attr.new_name, prefix=attr.prefix, category_id=category_id)


@category_router.patch("/remove_attr/{category_id}", response_model=GetCategory, responses={404: {"model": HTTPNotFoundError}})
async def remote_attr_in_category(category_id, remove_attrs: List[RemoveAttr]):
    '''Удаляет атрибут из фильтра категории и из всех товаров категории'''
    category = await Category.get(id=category_id)
    remove_attrs_for_sql = []
    for attr in remove_attrs:
       result = list(filter(lambda x: (x["name"] == attr.name), category.filters)) if category.filters else None
       if result:
           remove_attrs_for_sql.append(attr)
    for attr in remove_attrs_for_sql:
        await rowsql_remote_attrs_for_all_category(attr.name, category_id)


@category_router.delete("/{category_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_category(category_id: int):
    '''Удаляет категорию, для ее товаров в category_id становится null'''
    deleted_count = await Category.filter(id=category_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {category_id} not found")
    return Status(message=f"Deleted category {category_id}")


