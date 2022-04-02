from email.policy import default
from typing import Any
from tortoise import Tortoise, fields
from tortoise.models import Model
from decimal import Decimal
from tortoise.expressions import F
from pypika.terms import Function
from slugify import slugify

class Category(Model):
    id: int = fields.IntField(pk=True)
    name: str = fields.CharField(max_length=200, unique=True)
    parent: fields.ForeignKeyNullableRelation["Category"] = fields.ForeignKeyField(
        "models.Category", related_name="children", null=True, on_delete="SET NULL"
    )
    slug: str = fields.CharField(max_length=200, unique=True)
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

    async def save(self, *args, **kwargs):
        slug = slugify(self.name)
        self.slug = slug
        await super().save(*args, **kwargs)

    


class Product(Model):
    id: int = fields.IntField(pk=True)
    name: str = fields.CharField(max_length=200, unique=True)
    price: Decimal = fields.DecimalField(max_digits=1000, decimal_places=2)
    discount: Decimal = fields.DecimalField(max_digits=1000, decimal_places=2, default=0.0)
    category: fields.ForeignKeyNullableRelation["Category"] =  fields.ForeignKeyField("models.Category", related_name="products", null=True, on_delete="SET NULL")
    description: str = fields.TextField(default="")
    slug: str = fields.CharField(max_length=200, unique=True)
    photo = fields.JSONField(default=[])
    is_active = fields.BooleanField(default=False)
    # quantity: int = fields.IntField(default=0)
    attributes = fields.JSONField()
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    async def save(self, *args, **kwargs):
        slug = slugify(self.name)
        self.slug = slug
        await super().save(*args, **kwargs)



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


async def rowsql_append_filepath_photo_product(string_array: str, product_id: str):
    conn = Tortoise.get_connection("default")
    sql = f'''UPDATE product
             SET photo = photo || '{string_array}'::jsonb
             WHERE id = {product_id};'''
    await conn.execute_query(sql)

async def rowsql_remove_photo_product(string_qury: str, product_id: str):
    conn = Tortoise.get_connection("default")
    sql = f'''UPDATE product
             SET photo = photo - {string_qury}
             WHERE id = {product_id};'''
    await conn.execute_query(sql)


Tortoise.init_models(["app.catalog.models"], "models")
