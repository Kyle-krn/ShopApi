from aiogram import types
from main import dp


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer(f"Salom, {message.from_user.full_name}")