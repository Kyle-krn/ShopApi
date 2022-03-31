from fastapi_users import models
from fastapi_users.db import TortoiseBaseUserModel
from pydantic import EmailStr
from tortoise.contrib.pydantic import PydanticModel
from fastapi_users.db import TortoiseUserDatabase
# from models import UserDB, UserModel

class User(models.BaseUser):
    pass


class UserCreate(models.CreateUpdateDictModel):
    # is_verified = None
    email: EmailStr
    password: str
    pass


class UserUpdate(models.BaseUserUpdate):
    # is_verified = None
    pass


class UserModel(TortoiseBaseUserModel):
    # is_verified = None
    pass


class UserDB(User, models.BaseUserDB, PydanticModel):
    class Config:
        orm_mode = True
        orig_model = UserModel


async def get_user_db():
    yield TortoiseUserDatabase(UserDB, UserModel)