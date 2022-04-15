from decimal import Decimal
from tortoise import Tortoise, fields
from tortoise.models import Model
from app.catalog.models import Product


class TelegramOrder(Model):
    id: int = fields.IntField(pk=True)
    tg_id: int = fields.BigIntField()
    tg_username: int = fields.CharField(max_length=255)
    first_name: str = fields.CharField(max_length=200)
    last_name: str = fields.CharField(max_length=200, null=True)
    phone_number: str = fields.CharField(max_length=15)
    region: str = fields.CharField(max_length=255)
    city: str = fields.CharField(max_length=255)
    address1: str = fields.CharField(max_length=255)
    address2: str = fields.CharField(max_length=255, null=True)
    postcode: int = fields.IntField()
    products: fields.ReverseRelation["SaleProduct"]
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)


class SaleProduct(Model):
    id: int = fields.IntField(pk=True)
    product = fields.ForeignKeyNullableRelation = fields.ForeignKeyField("models.Product", related_name="sale_product", null=True, on_delete="SET NULL")
    price: Decimal = fields.DecimalField(max_digits=1000, decimal_places=2)
    discount: Decimal = fields.DecimalField(max_digits=1000, decimal_places=2, default=0.0)
    shipping_amount: Decimal = fields.DecimalField(max_digits=1000, decimal_places=2, default=0.0)
    name: str = fields.CharField(max_length=200, unique=True)
    quantity: int = fields.IntField()
    order: fields.ForeignKeyRelation = fields.ForeignKeyField("models.TelegramOrder", related_name="products")
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)


Tortoise.init_models(["app.orders.models"], "models")
