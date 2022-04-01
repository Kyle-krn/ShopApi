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
    description: str = fields.TextField(default="")
    # photo = fields.JSONField(null=True)
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


async def rowsql_add_attrs_for_all_category(sql_string_category: str, sql_string_product: str, category_id: int):
    conn = Tortoise.get_connection("default")
    # COALESCE(attributes, '[]'::jsonb)
    sql = f'''UPDATE product SET attributes = COALESCE(attributes, '[]'::jsonb) || {sql_string_product} WHERE category_id={category_id} '''
    await conn.execute_query(sql)
    sql = f'''UPDATE category SET filters = COALESCE(filters, '[]'::jsonb) || {sql_string_category} WHERE id = {category_id} '''
    await conn.execute_query(sql)


async def rowsql_remote_attrs_for_all_category(name: str, category_id: int):
    conn = Tortoise.get_connection("default")
    sql = '''UPDATE product SET attributes = remove_element(attributes, '{"name": "%s"}') WHERE category_id = %s''' % (name, category_id)
    await conn.execute_query(sql)
    
    sql = '''UPDATE category SET filters = remove_element(filters, '{"name": "%s"}') WHERE id = %s''' % (name, category_id)
    await conn.execute_query(sql)


async def rowsql_update_attr_name(old_name: str, new_name: str, prefix: str, category_id: int):
    conn = Tortoise.get_connection("default")
    sql = '''UPDATE product SET attributes = change_value(attributes, '{"name": "%s"}', '{"name": "%s"}') WHERE category_id = %s''' % (old_name, new_name, category_id)
    await conn.execute_query(sql)

    json_new_value_string = '{"name": "%s"}' % new_name
    if prefix:
        json_new_value_string = json_new_value_string[:-1] + ', "prefix": "%s"}' % prefix 
    
    sql = '''UPDATE category SET filters = change_value(filters, '{"name": "%s"}', '%s') WHERE id = %s''' % (old_name, json_new_value_string, category_id)
    await conn.execute_query(sql)

Tortoise.init_models(["app.catalog.models"], "models")
