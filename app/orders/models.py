from decimal import Decimal
from random import choices
from sqlalchemy import null
from tortoise import Tortoise, fields
from tortoise.models import Model
from app.catalog.models import Product
from app.delivery_settings.models import PickUpSettings
from tortoise.contrib.pydantic import pydantic_model_creator

SHIPPING_STATUS = ["Создано", "В обработке", "Отправлено", "В пункте самовывоза", "Получено"]


class TelegramOrder(Model):
    id: int = fields.IntField(pk=True)
    tg_id: int = fields.BigIntField()
    tg_username: str = fields.CharField(max_length=255)
    first_name: str = fields.CharField(max_length=200)
    last_name = fields.CharField(max_length=200, null=True)
    patronymic_name = fields.CharField(max_length=200, null=True)
    phone_number: str = fields.CharField(max_length=15)
    region = fields.CharField(max_length=255, null=True)
    city = fields.CharField(max_length=255, null=True)
    address1 = fields.CharField(max_length=255, null=True)
    address2 = fields.CharField(max_length=255, null=True)
    postcode = fields.IntField(null=True)
    products: fields.ReverseRelation["SaleProduct"]
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    shipping_type: str = fields.CharField(max_length=100)
    amount: Decimal = fields.DecimalField(max_digits=1000, decimal_places=2, null=True)
    shipping_amount: Decimal = fields.DecimalField(max_digits=1000, decimal_places=2, default=0.0)
    pickup_point: fields.ForeignKeyNullableRelation = fields.ForeignKeyField(
        "models.PickUpSettings", related_name="orders", null=True, on_delete="SET NULL"
    )
    pickup_code = fields.IntField(null=True)
    status = fields.CharField(max_length=255, choices=SHIPPING_STATUS, default="Создано")


class SaleProduct(Model):
    id: int = fields.IntField(pk=True)
    product: fields.ForeignKeyNullableRelation = fields.ForeignKeyField(
        "models.Product", related_name="sale_product", null=True, on_delete="SET NULL"
    )
    price: Decimal = fields.DecimalField(max_digits=1000, decimal_places=2)
    discount: Decimal = fields.DecimalField(max_digits=1000, decimal_places=2, default=0.0)
    name: str = fields.CharField(max_length=200)
    quantity: int = fields.IntField()
    order: fields.ForeignKeyRelation = fields.ForeignKeyField("models.TelegramOrder", related_name="products")
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)


Tortoise.init_models(["app.orders.models", "app.catalog.models"], "models")
