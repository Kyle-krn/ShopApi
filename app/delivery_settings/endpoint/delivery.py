from fastapi import APIRouter, HTTPException
from ..models import CourierCitySettings
from ..schemas import AddCourier, GetCourier
from settings import DADATA_TOKEN, DADATA_SECRET
from dadata import DadataAsync
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4)

router = APIRouter()


@router.get("/get-courier-city", response_model=GetCourier)
async def get_courier(city: str):
    city = await CourierCitySettings.filter(city=city)
    if city:
        return await GetCourier.from_tortoise_orm(city[0])
    else:
        raise HTTPException(status_code=400, detail=f"Город не найден.")


@router.post("/add-courier-city", status_code=200)
async def add_courier(courier: AddCourier):
    async with DadataAsync(DADATA_TOKEN, DADATA_SECRET) as dadata:
        resp = await dadata.clean(name="address", source=courier.city)
        if resp['result']:
            await CourierCitySettings.create(city=courier.city.capitalize(), amount=courier.amount)
        else:
            raise HTTPException(status_code=400, detail=f"Город не найден.")
        # print(resp['city'], resp['settlement'], resp['region'])
