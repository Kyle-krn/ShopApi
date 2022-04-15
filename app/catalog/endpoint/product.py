from fastapi import APIRouter, Depends, HTTPException
from tortoise.queryset import Q
from app.users.models import UserDB
from app.users.route import current_active_user, current_superuser
from ..models import Product, Category
from utils.row_sql.rowsql_query import rowsql_filtering_json_field
from ..schemas import GetProduct, CreateProduct, PaginationProduct, ProductAttr, UpdateProduct, validate_json_attr, Status, CategoryFilters, Images, QuryProducts
from tortoise.contrib.fastapi import HTTPNotFoundError
from typing import List
from fastapi import UploadFile
import os
from utils.utils import generate_random_string 
import aiofiles
import shutil


product_router = APIRouter()


@product_router.post("/create", response_model=GetProduct)
async def create_product(product: CreateProduct, user: UserDB = Depends(current_superuser)):
    '''Если не передать в теле запроса attributes : [] и у категории есть фильтры, то атрибуты автоматически добавятся со значением None'''
    category = await Category.get(id = product.category_id)
    children = category.children
    if len(await children) != 0:
        raise HTTPException(status_code=400, detail=f"Нельзя добавлять товар в категорию с подкатегориями.")
    try:
        # Продолжить здесь, сделать что бы можно было передавать только часть атрибутов и проверить что там с типами данных
        c_f = [CategoryFilters(name=i["name"], value=i["value"], prefix=i["prefix"]) for i in category.filters]
        if product.attributes:
            validate_json_attr(c_f, product.attributes)
            if len(product.attributes) < len(c_f):
                '''Если какие то атрибуты не переданы в теле запроса, но есть в фильтрах категории то автоматически добавятся со значением null'''
                for item in c_f:
                    result = list(filter(lambda x: (x.name == item.name), product.attributes))
                    if not result:
                        product.attributes.append(ProductAttr(name=item.name, value=None))
        else:
            def_attrs = [ProductAttr(name=i.name, value=None) for i in c_f]
            product.attributes = def_attrs
    except (IndexError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    product_obj = await Product.create(**product.dict())
    return await GetProduct.from_tortoise_orm(product_obj)


@product_router.post("/upload_photo/{product_id}", response_model=GetProduct, responses={404: {"model": HTTPNotFoundError}})
async def upload_photo_product(product_id: int, files: List[UploadFile], user: UserDB = Depends(current_superuser)):
    '''Добавление фото к товару, IMAGES_TYPES = ('jpg', 'jpeg', 'png')'''
    product = await Product.get(id=product_id)
    IMAGES_TYPES = ('jpg', 'jpeg', 'png')
    static_path = "static/"
    folder_path = f'product_img/{product.id}/'
    full_path = static_path + folder_path
    if os.path.exists(full_path) is False:
        os.mkdir(full_path)
    for file in files:
        if file.filename.split('.')[-1].lower() not in IMAGES_TYPES:
            continue
        filename = product.slug + "_" + await generate_random_string(6) + "." +file.filename.split('.')[-1]
        async with aiofiles.open(full_path + filename, 'wb') as out_file:
            content = await file.read()  # async read
            # if len(content) > 5242880:
            #     raise HTTPException(status_code=400, detail=f"Фото превышает 5 мб.")
            await out_file.write(content)
            product.photo.append(folder_path + filename)
    await product.save()

    return await GetProduct.from_tortoise_orm(await Product.get(id=product_id))


@product_router.post("/query_by_category/{category_id}", response_model=PaginationProduct, responses={404: {"model": HTTPNotFoundError}})
async def query_products(category_id: int, 
                         query:QuryProducts = None,
                         offset: int = 0,
                         limit: int = 20,
                         user: UserDB = Depends(current_active_user),):
    
    if query and query.attributes:
        x = await rowsql_filtering_json_field(category_id=category_id, query=query)
        get_product = []
        for i in x:
            del i['created_at']
            del i['updated_at']
            get_product.append(GetProduct(**i))
        return PaginationProduct(count=len(x), products=get_product)
        # for i in x:
            # return PaginationProduct(count=)
        return

    x = (Q(category_id=category_id) & Q(is_active=True))
    if query and query.min_price:
        x = x & Q(price__gte=query.min_price)
    if query and query.max_price:
        x = x & Q(price__lte=query.max_price)
    queryset = Product.filter(x).offset(offset).limit(limit)
    # print(await Product.filter(x)])
    # print(type(products))
    return PaginationProduct(count=await Product.filter(x).count(), products=await GetProduct.from_queryset(queryset))
    






@product_router.get("/all", response_model=List[GetProduct])
async def get_all_product(user: UserDB = Depends(current_active_user)):
    return await GetProduct.from_queryset(Product.all())


@product_router.get("/by_category/{category_id}", response_model=List[GetProduct], responses={404: {"model": HTTPNotFoundError}})
async def get_product_by_id(category_id, user: UserDB = Depends(current_active_user)):
    return await GetProduct.from_queryset(Product.filter(category_id=category_id))



@product_router.get("/{product_id}", response_model=GetProduct, responses={404: {"model": HTTPNotFoundError}})
async def get_product(product_id, user: UserDB = Depends(current_active_user)):
    # product_obj = await Product.get(id=product_id)
    # product_obj.weight = 99
    # await product_obj.save()
    return await GetProduct.from_tortoise_orm(await Product.get(id=product_id))






@product_router.delete("/delete_photo/{product_id}", response_model=GetProduct, responses={404: {"model": HTTPNotFoundError}})
async def delete_photo_product(product_id: int, delete_images: Images, user: UserDB = Depends(current_superuser)):
    product = await Product.get(id=product_id)
    delete_images = [i for i in delete_images.photo if i in product.photo]
    for img_name in delete_images:
        if os.path.exists(f'static/product_img/{str(product.id)}/{img_name}'):
            os.remove(f'static/product_img/{str(product.id)}/{img_name}')
        product.photo = [i for i in product.photo if i.split('/')[-1] != img_name]
    if product.photo == [] or product.photo is None:
        product.is_active = False
    await product.save()
    return await GetProduct.from_tortoise_orm(await Product.get(id=product_id))
    
        




@product_router.delete("/delete_all", response_model=Status)
async def delete_all_product(user: UserDB = Depends(current_superuser)):
    await Product.all().delete()
    return Status(message="Все товары удалены")



@product_router.delete("/{product_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_product(product_id, user: UserDB = Depends(current_superuser)):
    # Сделать отчистку атрибутов для удаленной категории
    deleted_count = await Product.get(id=product_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Товар #{product_id} не найден.")
    if os.path.exists(f'static/product_img/{str(product_id)}'):
        shutil.rmtree(f'static/product_img/{str(product_id)}')
    return Status(message=f"Товар {product_id} успешно удален.")




@product_router.patch("/{product_id}", response_model=GetProduct, responses={404: {"model": HTTPNotFoundError}})
async def update_product(product_id, update_product: UpdateProduct, user: UserDB = Depends(current_superuser)):
    """Что бы изменить порядок фото, нужно прислать массив по тому порядку который нужен"""
    product_obj = await Product.get(id=product_id)
    category = await product_obj.category
    print(update_product)
    if update_product.attributes:
        for attr in update_product.attributes:
            result = list(filter(lambda x: (x["name"] == attr.name), category.filters)) if category.filters else None
            if not result:
                raise HTTPException(status_code=404, detail=f"Атрибут {attr.name} не найден.")
            if type(attr.value) != type(result[0]["value"]) and attr.value is not None:
                raise HTTPException(status_code=404, detail=f"Атрибут {attr.name} ожидает тип {type(result[0]['value'])}.")
            product_value = next(i for i in product_obj.attributes if i["name"] == attr.name)
            product_value["value"] = attr.value
            if attr.prefix:
                product_value["prefix"] = attr.prefix
        await product_obj.save()
        del update_product.attributes
    
    if update_product.photo:
        if len(update_product.photo) != len(product_obj.photo):
            raise HTTPException(status_code=400, detail=f"Массивы не совпадают по количеству объектов.")
        for img in update_product.photo:
            if img not in product_obj.photo:
                raise HTTPException(status_code=400, detail=f"Фото {img} не найдено.")

    if update_product.is_active:
        if len(product_obj.photo) == 0:
            raise HTTPException(status_code=400, detail=f"Нельзя активировать товар без фото.")

    if update_product.category_id:
        category = await Category.get_or_none(id=update_product.category_id)
        if not category:
            raise HTTPException(status_code=400, detail=f"Категория #{update_product.category_id} не найдена.")
        if len(await category.children) > 0:
            raise HTTPException(status_code=400, detail=f"Нельзя добавлять товар в категорию с подкатегориями.")

    await product_obj.update_from_dict(update_product.dict(exclude_none=True))
    await product_obj.save()

    return await GetProduct.from_tortoise_orm(product_obj)

