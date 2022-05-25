from fastapi import APIRouter, Depends, HTTPException
from app.users.models import UserDB
from app.users.route import current_active_user, current_superuser
from ..models import Product, Category
from ..schemas import (CategoryFilters, ChangeNameAttr, GetCategory, CreateCategory, 
                      UpdateCategory, Status, RemoveAttr, CatalogWithActiveProduct, 
                      active_products_queryset, build_children)
from tortoise.contrib.fastapi import HTTPNotFoundError
from typing import List
from utils.row_sql.rowsql_query import (rowsql_add_attrs_for_all_category, rowsql_get_distinct_list_value, 
                                        rowsql_remote_attrs_for_all_category, rowsql_update_attr_name, 
                                        rowsql_get_distinct_string_value, rowsql_get_min_max_list_value, rowsql_get_min_max_price_discount)


category_router = APIRouter()

# Создать категорию
@category_router.post("/create", response_model=GetCategory)
async def category_route(category: CreateCategory, 
                         user: UserDB = Depends(current_superuser)):
    """Создать категорию. Нельзя добавлять в родительскую категорию категории которые имеют товары или фильтры к товарам
    """
    if category.parent_id is not None:
        parent_category_products = Product.filter(category_id=category.parent_id)
        if len(await parent_category_products) > 0:
            raise HTTPException(status_code=400, detail=f"Нельзя добавлять подкатегорию в категорию с товарами.")
        if (await Category.get(id=category.parent_id)).filters != []:
            raise HTTPException(status_code=400, detail=f"Нельзя добавлять подкатегорию в категорию с фильтрами.")

    category_obj = await Category.create(**category.dict())
    return await GetCategory.from_tortoise_orm(category_obj)


# GET 
@category_router.get("/main", response_model_include={List[CatalogWithActiveProduct], List[GetCategory]})
async def get_users(active: int = 0,
                    user: UserDB = Depends(current_active_user)):
    """Получить список категорий"""
    categories = await Category.filter(parent_id__isnull=True)
    if active:
        return [CatalogWithActiveProduct(id=category.id,
                                    name=category.name,
                                    slug=category.slug,
                                    parent_id=category.parent_id,
                                    filters=category.filters,
                                    products=await active_products_queryset(category.id),
                                    children=await build_children(await category.children, recursion_deep=3)) for category in categories]
    return await GetCategory.from_queryset(Category.filter(parent_id__isnull=True))



@category_router.get("/{category_id}", response_model_include={CatalogWithActiveProduct, GetCategory}, responses={404: {"model": HTTPNotFoundError}})
async def get_category(category_id: int, 
                       active: bool = False, 
                       user: UserDB = Depends(current_active_user)):
    """Получить категорию по id"""
    category = await Category.get(id=category_id)
    if active:
        return CatalogWithActiveProduct(id=category.id,
                                    name=category.name,
                                    slug=category.slug,
                                    parent_id=category.parent_id,
                                    filters=category.filters,
                                    products=await active_products_queryset(category_id),
                                    children=await build_children(await category.children, recursion_deep=3))
    return await GetCategory.from_tortoise_orm(await Category.get(id=category_id))


@category_router.get("/light/{category_id}", response_model=CatalogWithActiveProduct)
async def get_control_category(category_id, 
                               name: bool = False,
                               slug: bool = False,
                               filters: bool = False,
                               parent_id: bool = False,
                               children: bool = False,
                               children_count: bool = False,
                               products: bool = False,
                               products_count: bool = False,
                               user: UserDB = Depends(current_active_user)
                               ):
    '''Отдает настраиваемую модель категории'''
    category = await Category.get(id=category_id)
    response_model = CatalogWithActiveProduct(id=category.id)
    if name:
        response_model.name = category.name
    if slug:
        response_model.slug = category.slug
    if filters:
        response_model.filters = category.filters  
    if parent_id:
        response_model.parent_id = category.parent_id  
    if children:
        response_model.children = await build_children(await category.children, recursion_deep=3)
    if children_count:
        response_model.children_count = len(await build_children(await category.children, recursion_deep=3))
    if products:
        response_model.products = await active_products_queryset(category_id)
    if products_count:
        response_model.products_count = len(await active_products_queryset(category_id))
    return response_model
    

@category_router.get("/get_list_string_attr_value/{category_id}")
async def get_list_string_attr_value(category_id:int, 
                                     attr_name: str, 
                                     user: UserDB = Depends(current_active_user)):
    '''Отдает уникальные значение атриубта в товарах для всей категории'''
    category = await Category.get(id=category_id)
    filter = [i for i in category.filters if i['name'] == attr_name]
    if len(filter) == 0:
        raise HTTPException(status_code=400, detail=f"Атрибут {attr_name} не найден.")
    if type(filter[0]['value']) == str:
        queryset = await rowsql_get_distinct_string_value(category_id=category_id, attr_name=attr_name)
        return [i["value"] for i in queryset]
    elif type(filter[0]['value']) == list:
        queryset = await rowsql_get_distinct_list_value(category_id=category_id, attr_name=attr_name)
        return [i["value"].split('"')[1] for i in queryset]
    else:
        raise HTTPException(status_code=400, detail=f"Атрибут {attr_name} не list и не str.")

@category_router.get("/get_min_max_digit_attr_value/{category_id}")
async def get_min_max_digit_attr_value(category_id: int, 
                                       attr_name: str,
                                       user: UserDB = Depends(current_active_user)):
    """Отдает min max для числовых атрибутов"""
    category = await Category.get(id=category_id)
    filter = [i for i in category.filters if i['name'] == attr_name]
    if len(filter) == 0:
        raise HTTPException(status_code=400, detail=f"Атрибут {attr_name} не найден.")
    if type(filter[0]['value']) not in [int, float]:
        raise HTTPException(status_code=400, detail=f"Атрибут {attr_name} не float и не int.")
    queryset = await rowsql_get_min_max_list_value(category_id=category_id, attr_name=attr_name)
    return queryset[0]

@category_router.get("/min_max/{category_id}")
async def get_min_max_for_price_discount(category_id: int):
    """Отдает min max для price и discount"""
    queryset = await rowsql_get_min_max_price_discount(category_id=category_id)
    return queryset[0]

        
# PATCH
@category_router.patch("/{category_id}", response_model=GetCategory, responses={404: {"model": HTTPNotFoundError}})
async def patch_category(category_id: int, 
                         category: UpdateCategory, 
                         user: UserDB = Depends(current_superuser)):
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
        attr_for_product = [{"name":i.name, "value":None, "prefix": i.prefix} for i in category.filters]
        await Product.filter(category=category_obj).update(attributes=attr_for_product)
        
    elif category.filters == []:
        await Product.filter(category=category_obj).update(attributes=[])
    elif category.filters is None:
        del category.filters
        
    await category_obj.update_from_dict(category.dict(exclude_none=True))
    await category_obj.save()
    return await GetCategory.from_tortoise_orm(category_obj)


@category_router.patch("/add_attr/{category_id}", response_model=GetCategory, responses={404: {"model": HTTPNotFoundError}})
async def add_attr_in_category(category_id: int, 
                               category_attrs: List[CategoryFilters], 
                               user: UserDB = Depends(current_superuser)):
    '''Добавляет атрибуты в фильтры категории и автоматически добавляет атрибут ко всем товарам в категории со значением None, для bool значений передавайте строку "false" or "true"'''
    category = await Category.get(id=category_id)
    category_attrs_for_sql = []
    for attr in category_attrs:
        result = list(filter(lambda x: (x["name"] == attr.name), category.filters)) if category.filters else None
        if not result:
            '''Если в body передается атрибут который уже есть в фильтрах категории, он просто пропускается'''
            category_attrs_for_sql.append(attr)
    await rowsql_add_attrs_for_all_category(category_attrs_for_sql, category_id)
    
    return await GetCategory.from_tortoise_orm(await Category.get(id=category_id))


@category_router.patch("/change_attr/{category_id}", response_model=GetCategory, responses={404: {"model": HTTPNotFoundError}})
async def change_attr(category_id: int, 
                      data_attr: List[ChangeNameAttr], 
                      user: UserDB = Depends(current_superuser)):
    '''Изменяет имя или префикс фильтра и атрибутов'''
    category = await Category.get(id=category_id)
    category_attrs_for_sql = []
    for attr in data_attr:
        result = list(filter(lambda x: (x["name"] == attr.old_name), category.filters)) if category.filters else None
        if result:
            category_attrs_for_sql.append(attr)
    for attr in category_attrs_for_sql:
        await rowsql_update_attr_name(old_name=attr.old_name, new_name=attr.new_name, prefix=attr.prefix, category_id=category_id)
    return await GetCategory.from_tortoise_orm(await Category.get(id=category_id))


@category_router.patch("/remove_attr/{category_id}", response_model=GetCategory, responses={404: {"model": HTTPNotFoundError}})
async def remote_attr_in_category(category_id: int, 
                                  remove_attrs: List[RemoveAttr], 
                                  user: UserDB = Depends(current_superuser)):
    '''Удаляет атрибут из фильтра категории и из всех товаров категории'''
    category = await Category.get(id=category_id)
    remove_attrs_for_sql = []
    for attr in remove_attrs:
       result = list(filter(lambda x: (x["name"] == attr.name), category.filters)) if category.filters else None
       if result:
           remove_attrs_for_sql.append(attr)
    for attr in remove_attrs_for_sql:
        await rowsql_remote_attrs_for_all_category(attr.name, category_id)
    return await GetCategory.from_tortoise_orm(await Category.get(id=category_id))


# DELETE
@category_router.delete("/{category_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_category(category_id: int, 
                          user: UserDB = Depends(current_superuser)):
    '''Удаляет категорию, для ее товаров в category_id становится null'''
    deleted_count = await Category.filter(id=category_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {category_id} not found")
    return Status(message=f"Deleted category {category_id}")


