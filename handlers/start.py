from loader import db, dp 
from aiogram import Router, types, F 
from aiogram.filters import CommandStart


r = Router(name='start')
dp.include_router(r)



@r.message(CommandStart())
async def command_start(update: types.Message):
    await update.answer("Hi")


@r.message()
async def main_message(update: types.Message):
    await update.answer("Hi2")

@r.callback_query(F.data == "check")
async def check(update: types.CallbackQuery):
    await update.answer("✅ Botdan foydalanishingiz mumkin !")

    try:
        await update.message.delete()
    except:
        pass

    await update.message.answer("✅ Botdan foydalanishingiz mumkin !")