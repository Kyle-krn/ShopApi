from pydantic import BaseModel, validator
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel
from .models import CourierCitySettings

class AddCourier(BaseModel):
    city: str
    amount: int


GetCourier = pydantic_model_creator(CourierCitySettings, name="Courier")
