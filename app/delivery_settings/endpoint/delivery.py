from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.users.route import current_active_user, current_superuser
from app.users.models import UserDB
from ..models import CourierCitySettings, PickUpSettings
from ..schemas import AddCourier, GetCourier, AddPickUp, GetPickUp
from settings import DADATA_TOKEN, DADATA_SECRET
from dadata import DadataAsync
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4)

router = APIRouter()


@router.get("/get-courier-city", response_model=GetCourier)
async def get_courier(city: str, 
                      user: UserDB = Depends(current_active_user)):
    """Получить список городов где работает курьерская доставка"""
    city = await CourierCitySettings.filter(city=city)
    if city:
        return await GetCourier.from_tortoise_orm(city[0])
    else:
        raise HTTPException(status_code=400, detail=f"Город не найден.")


@router.post("/add-courier-city", status_code=200)
async def add_courier(courier: AddCourier,
                      user: UserDB = Depends(current_superuser)):
    """Добавить курьерскую доставку в город"""
    async with DadataAsync(DADATA_TOKEN, DADATA_SECRET) as dadata:
        resp = await dadata.clean(name="address", source=courier.city)
        if resp['result']:
            await CourierCitySettings.create(city=courier.city.capitalize(), amount=courier.amount)
        else:
            raise HTTPException(status_code=400, detail=f"Город не найден.")
        # print(resp['city'], resp['settlement'], resp['region'])


@router.get("/get-pickup-point/{pp_id}", response_model=GetPickUp)
async def get_pickup_point(pp_id: int,
                           user: UserDB = Depends(current_active_user)):
    """Получить инфу о пункте самовывоза"""
    return await GetPickUp.from_tortoise_orm(await PickUpSettings.get(id=pp_id))


@router.get("/get-city-pickup-point", response_model=List[GetPickUp])
async def get_pickup_point(city: str,
                           user: UserDB = Depends(current_active_user)):
    """Поиск ПП по городу"""
    return await GetPickUp.from_queryset(PickUpSettings.filter(city=city))


@router.get("/get-distinct-city-pickup-point")
async def get_distinct_pickup_point(user: UserDB = Depends(current_active_user)):
    """Вернуть список городов с ПП"""
    return [i['city'] for i in await PickUpSettings.all().distinct().values('city')]


@router.post("/add-pickup-point", status_code=200)
async def add_pickup_point(pickup: AddPickUp, 
                           user: UserDB = Depends(current_superuser)):
    """Добавить ПП"""
    async with DadataAsync(DADATA_TOKEN, DADATA_SECRET) as dadata:
        resp = await dadata.clean(name="address", source=f"{pickup.city} {pickup.address}")
    if not resp['result']:
        raise HTTPException(status_code=400, detail=f"Адрес не найден.")
    await PickUpSettings.create(city=pickup.city.capitalize(), 
                                address=pickup.address.capitalize(), 
                                latitude=resp['geo_lat'], 
                                longitude=resp['geo_lon'])
