from email.policy import default
import imp
from typing import Any
from unicodedata import category
from xml.etree.ElementInclude import include
from attr import attributes
from tortoise import Tortoise, fields
from tortoise.models import Model
from decimal import Decimal
from tortoise.expressions import F
from pypika.terms import Function

class Category(Model):
    id: int = fields.IntField(pk=True)
    name: str = fields.CharField(max_length=200)
    parent: fields.ForeignKeyNullableRelation["Category"] = fields.ForeignKeyField(
        "models.Category", related_name="children", null=True, on_delete="SET NULL"
    )
    children: fields.ReverseRelation["Category"]
    products: fields.ReverseRelation["Product"]
    filters = fields.JSONField(null=True)
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class PydanticMeta:
        # computed = ["name_length", "team_size", "not_annotated"]
        exclude = ["parent", "updated_at", "created_at", "products.category"]
        allow_cycles = True
        max_recursion = 4


class Product(Model):
    id: int = fields.IntField(pk=True)
    name: str = fields.CharField(max_length=200)
    price: Decimal = fields.DecimalField(max_digits=1000, decimal_places=2)
    discount: Decimal = fields.DecimalField(max_digits=1000, decimal_places=2, default=0.0)
    category: fields.ForeignKeyNullableRelation["Category"] =  fields.ForeignKeyField("models.Category", related_name="products", null=True, on_delete="SET NULL")
    # category_id: int
    description: str = fields.TextField()
    attributes = fields.JSONField()
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class PydanticMeta:
        # computed = ["category_id"]
        exclude = ["updated_at", "created_at", "category.children"]
        # include = ["category"]
        # allow_cycles = True
        # max_recursion = 4



class JsonbSet(Function):
    def __init__(self, field: F, path: str, value: Any, create_if_missing: bool = False):
        super().__init__("jsonb_set", field, path, value, create_if_missing)


Tortoise.init_models(["app.catalog.models"], "models")
