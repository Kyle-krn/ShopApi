from tortoise import Tortoise, fields
from tortoise.models import Model
from decimal import Decimal
from slugify import slugify
# import app.orders.models

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
        exclude = ["updated_at", "created_at", "products.category", "children.parent", "parent", "parent.children", "parent.products", "parent.filters"]
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
    quantity: int = fields.IntField(default=0)
    attributes = fields.JSONField()
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    weight: int = fields.IntField() # Вес в граммах
    # sales: fields.ReverseRelation["app.orders.models.SaleProduct"]

    async def save(self, *args, **kwargs):
        slug = slugify(self.name)
        self.slug = slug
        await super().save(*args, **kwargs)


    class PydanticMeta:
        exclude = ["updated_at", "created_at", "category"]




Tortoise.init_models(["app.catalog.models"], "models")
