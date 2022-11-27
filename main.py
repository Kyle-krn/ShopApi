from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
import settings
from app import routers
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(routers.api_router)

register_tortoise(
    app,
    db_url=f"postgres://{settings.USER}:{settings.PASSWORD}@{settings.HOST}:{settings.PORT}/{settings.DATABASE}",
    modules={"models": settings.APPS_MODELS},
    generate_schemas=True,
    add_exception_handlers=True,
)
