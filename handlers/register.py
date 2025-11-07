from loader import db, dp, bot
from aiogram import Router, types, F 
from aiogram.filters import CommandStart, CommandObject, StateFilter
from asyncio import Semaphore
from states import UserStates, RegisterStates
from aiogram.fsm.context import FSMContext
from buttons import KeyboardButtons, InlineButtons
from utils import can_edit, check_number
from db import User
from .context import start_registring, SEND_NUMBER_MESSAGE, MAIN_MESSAGE

r = Router(name='start')
dp.include_router(r)
register = Semaphore()


@r.callback_query(F.data == "check2", RegisterStates.check_sub)
async def check_sub(update: types.CallbackQuery, state: FSMContext):
    chanels = []
    for chanel in db.chanels:
        if not await is_subscribed(update.from_user.id, chanel.get('id')):
            chanels.append(chanel)
    
    if chanels:
        await update.answer("❗️ Iltimos kanalmizga obuna bo'ling", show_alert=True)
    else:
        await delete_callback(update)
        await update.message.answer(SEND_NUMBER_MESSAGE, reply_markup=KeyboardButtons.SEND_MY_NUMBER)
        await state.set_state(RegisterStates.get_number)

async def delete_callback(update: types.CallbackQuery):
    if can_edit(update.message.date):
        await update.message.delete()
    else:
        await update.message.edit_reply_markup(reply_markup=None)


@r.message(StateFilter(RegisterStates.check_sub))
async def check_message_sub(update: types.Message, state: FSMContext):
    chanels = []
    for chanel in db.chanels:
        if not await is_subscribed(update.from_user.id, chanel.get('id')):
            chanels.append(chanel)
    
    if chanels:
        await update.answer("❗️ Iltimos kanalmizga obuna bo'ling", reply_markup=InlineButtons.chanels(chanels))
    
    else:
        await update.answer(SEND_NUMBER_MESSAGE, reply_markup=KeyboardButtons.SEND_MY_NUMBER)
        await state.set_state(RegisterStates.get_number)




@r.message(StateFilter(RegisterStates.get_number))
async def get_number(update: types.Message, state: FSMContext):
    if update.contact:
        number = update.contact.phone_number
    
    elif update.text and check_number(update.text):
        number = update.text

    else:
        return await update.answer("❗️ Iltimos \"📲 Telefon raqamimni yuborish\" tugmasini bosing yoki +998951234567, 998951234567, 951234567 ko‘nishda raqamingizni yuboring.", reply_markup=KeyboardButtons.SEND_MY_NUMBER)

    state_data = await state.get_data()
    invater = state_data.get('invater')
    await state.clear()
    await register_user(update, invater, number)
    



async def register_user(update: types.Message, invater: User, number: str):
    async with register:
        user = await db.get_user(update.from_user.id)
        if user:
            return
        
        user = User(id = update.from_user.id, 
                    first_name=update.from_user.first_name, 
                    last_name=update.from_user.last_name, 
                    phone_number=number)
        await db.register_user(user)
        if invater:
            i = await db.get_user(invater.id)
            i.invited_users += 1
            await db.update_user(i.id, invited_users = i.invited_users)
    
    await update.answer(f"{update.from_user.first_name} siz konkursimiz ishtrokchisiz!", reply_markup=KeyboardButtons.HOME)
    await update.answer(MAIN_MESSAGE, reply_markup=InlineButtons.HOME)

    if invater:
        await bot.send_message(text = f"Sizning havolangiz orqali {update.from_user.first_name} botdan royxatdan o'tdi. Jami taklif qilgan dostlaringiz {i.invited_users} ta.",
                               chat_id = invater.id)



async def is_subscribed(user_id : int, chanel : str):
    try:
        member  = await bot.get_chat_member(chat_id = chanel, user_id = user_id)
        if member and member.status != 'left':
            return True
        return False  
    except Exception as e:
        return False
