from pydantic import BaseModel, validator
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel
from .models import CourierCitySettings, PickUpSettings

class AddCourier(BaseModel):
    city: str
    amount: int


class AddPickUp(BaseModel):
    city: str
    address: str


class DistinctPickUpCity(BaseModel):
    city: str


GetCourier = pydantic_model_creator(CourierCitySettings, name="Courier")
GetPickUp = pydantic_model_creator(PickUpSettings, name="PickUp")
