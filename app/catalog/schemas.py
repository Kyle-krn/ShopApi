from __future__ import annotations
from typing import Any, List, Optional
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel
from .models import Category, Product
from pydantic import BaseModel, validator
from tortoise.queryset import Q

GetCategory = pydantic_model_creator(Category, name="Category")
GetProduct = pydantic_model_creator(Product, name="Product")


class CatalogWithActiveProduct(BaseModel):
    """Модель для того что бы не нагружать лишней информацией запросы от бота"""

    id: int
    name: Optional[str]
    slug: Optional[str]
    parent_id: Optional[int] = None
    filters: Optional[list]
    children: Optional[List["CatalogWithActiveProduct"]]
    children_count: Optional[int]
    products: Optional[List[GetProduct]]
    products_count: Optional[int]


async def active_products_queryset(category_id):
    """Не могу поместить эту херню в models из за ошибки импорта"""
    return await GetProduct.from_queryset(Product.filter(Q(category_id=category_id) & Q(is_active=True)))


async def build_children(category_list: List[Category], recursion_deep: int, active_product: bool = True):
    """Как задать запрос для вложенных товаров я не нашел, так что эта рекурсивная функция генерит рекурсивный каталог где только активные товары"""
    if recursion_deep == 1:
        return None
    if category_list == []:
        return []
    return [
        CatalogWithActiveProduct(
            id=i.id,
            name=i.name,
            slug=i.slug,
            parent_id=i.parent_id,
            filters=i.filters,
            products=await active_products_queryset(i.id),
            children=await build_children(await i.children, recursion_deep=recursion_deep - 1),
        )
        for i in category_list
    ]


class ProductAttr(PydanticModel):
    """Модель атрибутов товара"""

    name: str
    value: Any
    prefix: str = None

    @validator("value", pre=True)
    def split_str(cls, v):
        if type(v) in [list, int, float, bool, str]:
            return v
        elif v is None:
            return None
        raise ValueError("Only list, int, float, bool, str")


class CategoryFilters(ProductAttr):
    """Модель фильтров категории"""

    value: Any

    @validator("value", pre=True)
    def split_str(cls, v):
        if type(v) == list:
            return []
        elif type(v) == int:
            return 1
        elif type(v) == float:
            return 1.1
        elif type(v) == bool:
            return True
        elif type(v) == str:
            return ""
        raise ValueError("Only list, int, float, bool, str")


class RemoveAttr(PydanticModel):
    name: str


class ChangeNameAttr(PydanticModel):
    old_name: str
    new_name: str
    prefix: Optional[str]


class CreateCategory(PydanticModel):
    name: str
    parent_id: int = None
    filters: List[CategoryFilters] = []

    @validator("filters", pre=True)
    def check_filter_item(cls, v):
        # print(v)
        for item in v:
            item_find = list(filter(lambda x: (x["name"] == item["name"]), v))
            if len(item_find) > 1:
                raise ValueError(f"Атрибут {item['name']} повторяется.")
        return v


class UpdateCategory(PydanticModel):
    name: Optional[str]
    parent_id: Optional[int] = None
    filters: Optional[List[CategoryFilters]]

    @validator("filters", pre=True)
    def check_filter_item(cls, v):
        # print(v)
        for item in v:
            item_find = list(filter(lambda x: (x["name"] == item["name"]), v))
            if len(item_find) > 1:
                raise ValueError(f"Атрибут {item['name']} повторяется.")
        return v


class Status(BaseModel):
    message: str


class PaginationProduct(BaseModel):
    count: int
    products: List[GetProduct]


class QuryProducts(BaseModel):
    min_price: Optional[float]
    max_price: Optional[float]
    attributes: Optional[list]


class UpdateProduct(PydanticModel):
    name: Optional[str]
    price: Optional[float]
    discount: Optional[float]
    category_id: Optional[int]
    description: Optional[str]
    is_active: Optional[bool]
    attributes: Optional[List[ProductAttr]]
    photo: Optional[List[str]]

    @validator("attributes", pre=True)
    def check_filter_item(cls, v):
        # print(v)
        for item in v:
            item_find = list(filter(lambda x: (x["name"] == item["name"]), v))
            if len(item_find) > 1:
                raise ValueError(f"Атрибут {item['name']} повторяется.")
        return v


class CreateProduct(PydanticModel):
    name: str
    price: float
    discount: Optional[float] = 0.0
    description: Optional[str]
    category_id: int
    attributes: Optional[List[ProductAttr]]
    weight: int

    @validator("attributes", pre=True)
    def check_filter_item(cls, v):
        # print(v)
        for item in v:
            item_find = list(filter(lambda x: (x["name"] == item["name"]), v))
            if len(item_find) > 1:
                raise ValueError(f"Атрибут {item['name']} повторяется.")
        return v


class Images(PydanticModel):
    photo: list


def validate_json_attr(attr_category: CategoryFilters, attr_product: ProductAttr):
    if len(attr_product) > len(attr_category):
        raise IndexError(f"Должно быть {len(attr_category)} атрибутов.")
    for attr in attr_product:
        product_type = type(attr.value)
        result = list(filter(lambda x: (x.name == attr.name), attr_category))
        if not result:
            raise IndexError(f"Атрибут {attr.name} не найден в фильтрах категории.")
        category_type = type(result[0].value)
        if category_type != product_type:
            raise TypeError(f"Атрибут '{attr.name}' ожидает тип {category_type}")
