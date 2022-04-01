from sys import prefix
from typing import Any, List, Optional, Type, Union
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel
from .models import Category, Product


GetCategory = pydantic_model_creator(Category, name="Category")


class ProductAttr(PydanticModel):
    name: str
    value: Union[int, float, bool, str, list] = None



class CategoryFilters(ProductAttr):
    prefix: str
    value: Union[int, float, bool, str, list]


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
    # filters: Optional[list] = []


class UpdateCategory(PydanticModel):
    name: Optional[str]
    parent_id: Optional[int] = None
    filters: Optional[List[CategoryFilters]]



class Status(BaseModel):
    message: str


GetProduct = pydantic_model_creator(Product, name="Product")



class UpdateProduct(PydanticModel):
    name: Optional[str]
    price: Optional[float]
    discount: Optional[float]
    category_id: Optional[int]
    attributes: Optional[List[ProductAttr]]


class CreateProduct(PydanticModel):
    name: str
    price: float
    discount: Optional[float] = 0.0
    description: Optional[str]
    category_id: int
    attributes: Optional[List[ProductAttr]]


def validate_json_attr(attr_category, attr_product):
    tuple_attr_category = tuple([i.name for i in attr_category]) if attr_category else None
    tuple_attr_product = tuple([i.name for i in attr_product]) if attr_product else None
    if tuple_attr_product != tuple_attr_category:
        raise IndexError("Атрибуты категории и товара не совпадают")


    for attr in attr_category:
        category_type = type(attr.value)
        result = list(filter(lambda x: (x.name == attr.name), attr_product))
        product_type = type(result[0].value)
        if category_type != product_type:
            raise TypeError(f"Атрибут '{attr.name}' ожидает тип {category_type}")

