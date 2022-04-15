from tortoise import Tortoise, fields
from tortoise.models import Model


class CourierCitySettings(Model):
    id: int = fields.IntField(pk=True)
    city: str = fields.CharField(max_length=255)
    amount: int = fields.IntField()


class PickUpSettings(Model):
    id: int = fields.IntField(pk=True)
    city: str = fields.CharField(max_length=255)
    address: str = fields.CharField(max_length=255) 
    latitude: str = fields.FloatField()
    longitude: str = fields.FloatField()
    # address1: str = fields.CharField(max_length=255) 
    # latitude longitude


Tortoise.init_models(["app.delivery_settings.models"], "models")
