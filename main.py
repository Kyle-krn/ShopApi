import asyncio
from fastapi import FastAPI
from aiogram import Dispatcher, Bot
from settings import BOT_TOKEN
from fastapi import FastAPI
# from fastapi_users import FastAPIUsers
# from models import get_user_manager, auth_backend, User,UserCreate, UserUpdate, UserDB
from tortoise.contrib.fastapi import register_tortoise
import settings
# from tortoise import Tortoise
from app import routers
# fastapi_users = FastAPIUsers(
#     get_user_manager,
#     [auth_backend],
#     User,
#     UserCreate,
#     UserUpdate,
#     UserDB,
# )

# current_active_user = fastapi_users.current_user(active=True)


app = FastAPI()

app.include_router(routers.api_router)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)






# from api import on_startup, on_shutdown, bot_webhook
# from bot import start



register_tortoise(      app,
                        db_url=f"postgres://{settings.USER}:{settings.PASSWORD}@{settings.HOST}:{settings.PORT}/{settings.DATABASE}",
                        modules={"models": settings.APPS_MODELS},
                        generate_schemas=True,
                        add_exception_handlers=True,
                        )
# Tortoise.init_models(APPS_MODELS, 'models')
# async def start_row_db():


# asyncio.create_task(start_row_db())

# if __name__ == "__main__":
#     await Users.create()