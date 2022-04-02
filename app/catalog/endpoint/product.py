from fastapi import APIRouter, HTTPException
from ..models import Product, Category, rowsql_append_filepath_photo_product, rowsql_remove_photo_product
from ..schemas import GetProduct, CreateProduct, ProductAttr, UpdateProduct, validate_json_attr, Status, CategoryFilters, Images
from tortoise.contrib.fastapi import HTTPNotFoundError
from typing import List
from fastapi import UploadFile
import os
from utils.utils import generate_random_string, generate_string_array_for_sql, generate_query_for_sql
import aiofiles
product_router = APIRouter()


@product_router.post("/create", response_model=GetProduct)
async def create_product(product: CreateProduct):
    '''Если не передать в теле запроса attributes : [] и у категории есть фильтры, то атрибуты автоматически добавятся со значением None'''
    category = await Category.get(id = product.category_id)
    children = category.children
    if len(await children) != 0:
        raise HTTPException(status_code=400, detail=f"Нельзя добавлять товар в категорию с подкатегориями.")
    try:
        c_f = [CategoryFilters(name=i["name"], value=i["value"], prefix=i["prefix"]) for i in category.filters]
        if product.attributes:
            validate_json_attr(c_f, product.attributes)
        else:
            def_attrs = [ProductAttr(name=i.name, value=None) for i in c_f]
            product.attributes = def_attrs
    except (IndexError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    product_obj = await Product.create(**product.dict())
    return await GetProduct.from_tortoise_orm(product_obj)


@product_router.post("/upload_photo/{product_id}", response_model=GetProduct, responses={404: {"model": HTTPNotFoundError}})
async def upload_photo_product(product_id: int, files: List[UploadFile]):
    '''Добавление фото к товару, IMAGES_TYPES = ('jpg', 'jpeg', 'png')'''
    product = await Product.get(id=product_id)
    IMAGES_TYPES = ('jpg', 'jpeg', 'png')
    static_path = "static/"
    folder_path = f'product_img/{product.id}/'
    full_path = static_path + folder_path
    if os.path.exists(full_path) is False:
        os.mkdir(full_path)
    img_path_list = []
    for file in files:
        if file.filename.split('.')[-1].lower() not in IMAGES_TYPES:
            continue
        filename = product.slug + "_" + await generate_random_string(6) + "." +file.filename.split('.')[-1]
        async with aiofiles.open(full_path + filename, 'wb') as out_file:
            content = await file.read()  # async read
            # if len(content) > 5242880:
            #     raise HTTPException(status_code=400, detail=f"Фото превышает 5 мб.")
            await out_file.write(content)
        img_path_list.append(filename)
    if img_path_list:
        string_array = await generate_string_array_for_sql(img_path_list)
        await rowsql_append_filepath_photo_product(string_array, product_id)
    return await GetProduct.from_tortoise_orm(await Product.get(id=product_id))


# @product_router.patch("/change_img/{product_id}", response_model=GetProduct, responses={404: {"model": HTTPNotFoundError}})
# async def change_photo_product(product_id: int, array_img: Images):
#     product = await Product.get(id=product_id)
#     if len(array_img.photo) != len(product.photo):
#         raise HTTPException(status_code=400, detail=f"Массивы не совпадают по количеству объектов.")
#     for img in array_img.photo:
#         if img not in product.photo:
#             raise HTTPException(status_code=400, detail=f"Фото {img} не найдено.")
#     product.photo = array_img.photo
#     await product.save()
#     return await GetProduct.from_tortoise_orm(product)



@product_router.delete("/delete_photo/{product_id}", response_model=GetProduct, responses={404: {"model": HTTPNotFoundError}})
async def delete_photo_product(product_id: int, delete_images: Images):
    product = await Product.get(id=product_id)
    delete_imagess = [i for i in delete_images.photo if i in product.photo]
    for img_name in delete_images.photo:
        if os.path.exists(f'static/product_img/{str(product.id)}/{img_name}'):
            os.remove(f'static/product_img/{str(product.id)}/{img_name}')
    string_array = await generate_query_for_sql(delete_imagess)
    if string_array:
        await rowsql_remove_photo_product(string_array, product_id)
    return await GetProduct.from_tortoise_orm(await Product.get(id=product_id))
    
        




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
async def update_product(product_id, update_product: UpdateProduct):
    """Что бы изменить порядок фото, нужно прислать массив по тому порядку который нужен"""
    product_obj = await Product.get(id=product_id)
    category = await product_obj.category
    print(update_product)
    if update_product.attributes:
        for attr in update_product.attributes:
            result = list(filter(lambda x: (x["name"] == attr.name), category.filters)) if category.filters else None
            if not result:
                raise HTTPException(status_code=404, detail=f"Атрибут {attr.name} не найден.")
            if type(attr.value) != type(result[0]["value"]):
                raise HTTPException(status_code=404, detail=f"Атрибут {attr.name} ожидает тип {type(result[0]['value'])}.")
            product_value = next(i for i in product_obj.attributes if i["name"] == attr.name)
            product_value["value"] = attr.value
        # await product_obj.save()
        del update_product.attributes
    
    if update_product.photo:
        if len(update_product.photo) != len(product_obj.photo):
            raise HTTPException(status_code=400, detail=f"Массивы не совпадают по количеству объектов.")
        for img in update_product.photo:
            if img not in product_obj.photo:
                raise HTTPException(status_code=400, detail=f"Фото {img} не найдено.")      
    if update_product.is_active:
        if len(product_obj.photo):
            raise HTTPException(status_code=400, detail=f"Нельзя активировать товар без фото.")

    await product_obj.update_from_dict(update_product.dict(exclude_none=True))
    await product_obj.save()

    return await GetProduct.from_tortoise_orm(product_obj)



@product_router.get("/{product_id}", response_model=GetProduct, responses={404: {"model": HTTPNotFoundError}})
async def get_product(product_id):
    # product_obj = await Product.get(id=product_id)
    return await GetProduct.from_tortoise_orm(await Product.get(id=product_id))