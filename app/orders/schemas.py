from typing import List
from pydantic import BaseModel, validator
from tortoise import Tortoise
from .models import TelegramOrder, SaleProduct
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel

GetOrder = pydantic_model_creator(TelegramOrder, name="TelegramOrder")

class SalesProducts(BaseModel):
    id: int
    quantity: int


class CreateTelegramOrder(BaseModel):
    tg_id: int
    tg_username: str = None
    first_name: str 
    last_name: str = None
    patronymic_name: str = None
    phone_number: str 
    region: str 
    city: str 
    address1: str 
    address2: str = None
    postcode: int
    shipping_type: str
    shipping_amount: int
    amount: float
    products: List[SalesProducts]


class GetPPOrder(BaseModel):
    message: str
    code: int


class CreatePPOrder(BaseModel):
    tg_id: int
    tg_username: str = None
    first_name: str 
    last_name: str = None
    patronymic_name: str = None
    phone_number: str 
    shipping_type: str
    # shipping_amount: int
    amount: float
    products: List[SalesProducts]
    pickup_point_id: int
    



