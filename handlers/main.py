from loader import db, dp, bot
from aiogram import Router, types, F 
from aiogram.filters import CommandStart
from asyncio import Semaphore
from states import UserStates
from aiogram.fsm.context import FSMContext
from buttons import KeyboardButtons
from utils import can_edit
from .start import SEND_NUMER_MESSAGE

r = Router(name='main')
dp.include_router(r)
register = Semaphore()

@r.message()
async def main_message(update: types.Message, state: FSMContext):
    user = await db.get_user(update.from_user.id)
    if not user:
        await state.set_state(UserStates.get_number)
        await update.answer(SEND_NUMER_MESSAGE, reply_markup=KeyboardButtons.SEND_MY_NUMBER)
        return
    
    if update.text == "👥 Taklif qilgan do'stlarim":
        await update.answer("siz {n}ta do'stingizni taklif qildingiz".format(n=user.invited_users),
                            reply_markup=KeyboardButtons.HOME)
    
    elif update.text == "🔗 Maxsus havolam":
        url = f"https://t.me/{db.bot.username}?start={user.id}"
        await bot.copy_message(chat_id=update.from_user.id,
                               from_chat_id=db.DATA_CHANEL_ID,
                               message_id=5,
                               caption="sizning havolangiz \n{url}".format(url = url),
                               reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                   [types.InlineKeyboardButton(text="Ishtrok etish", url=url)]
                               ]))
        
    else:
        await update.answer("salom", reply_markup=KeyboardButtons.HOME)
        