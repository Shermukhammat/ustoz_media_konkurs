from loader import db, dp, bot
from aiogram import Router, types, F 
from aiogram.filters import CommandStart
from asyncio import Semaphore
from states import UserStates
from aiogram.fsm.context import FSMContext
from buttons import KeyboardButtons, InlineButtons
from utils import can_edit
from .context import start_registring, MAIN_MESSAGE

r = Router(name='main')
dp.include_router(r)
register = Semaphore()
INVATE_POST_TEXT = "Konkursda qatnashish uchun quyidagi havola orqali o'ting 👇👇👇 {url}"

@r.message()
async def main_message(update: types.Message, state: FSMContext):
    user = await db.get_user(update.from_user.id)
    if not user:
        return await start_registring(update, state)
    
    if update.text == "👥 Taklif qilgan do'stlarim":
        await update.answer("siz {n}ta do'stingizni taklif qildingiz".format(n=user.invited_users),
                            reply_markup=KeyboardButtons.HOME)
    
    elif update.text == "🔗 Maxsus havolam":
        url = f"https://t.me/{db.bot.username}?start={user.id}"
        msg = await bot.copy_message(chat_id=update.from_user.id,
                               from_chat_id=db.DATA_CHANEL_ID,
                               message_id=5,
                               caption=INVATE_POST_TEXT.format(url = url),
                               reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                   [types.InlineKeyboardButton(text="Ishtrok etish", url=url)]
                               ]))
        
        await bot.send_message(chat_id=update.from_user.id,
                               reply_to_message_id=msg.message_id,
                               reply_markup=KeyboardButtons.HOME,
                               text="👆👆👆 Bu postda sizning shaxsiy linkingiz joylashgan \n\nYuqoridagi postni yaqinlaringizga tarqating, ular sizning linkingizni bosib botga start berishi va telegram kanalga obuna bo’lishi kerak.")
        
    else:
        await update.answer(MAIN_MESSAGE.format(name=user.first_name, bot=db.bot.full_name), reply_markup=InlineButtons.HOME)
        


@r.callback_query(F.data == "url")
async def url(update: types.CallbackQuery, state: FSMContext):
    user = await db.get_user(update.from_user.id)
    if user:
        await update.answer()
        url = f"https://t.me/{db.bot.username}?start={user.id}"
        msg = await bot.copy_message(chat_id=update.from_user.id,
                               from_chat_id=db.DATA_CHANEL_ID,
                               message_id=5,
                               caption=INVATE_POST_TEXT.format(url = url),
                               reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                   [types.InlineKeyboardButton(text="Ishtrok etish", url=url)]
                               ]))
        await bot.send_message(chat_id=update.from_user.id,
                               reply_to_message_id=msg.message_id,
                               text="👆👆👆 Bu postda sizning shaxsiy linkingiz joylashgan \n\nYuqoridagi postni yaqinlaringizga tarqating, ular sizning linkingizni bosib botga start berishi va telegram kanalga obuna bo’lishi kerak.")