from loader import db, dp, bot, context
from aiogram import Router, types, F 
from aiogram.filters import CommandStart, CommandObject, StateFilter
from asyncio import Semaphore
from states import UserStates, RegisterStates
from aiogram.fsm.context import FSMContext
from buttons import KeyboardButtons, InlineButtons
from utils import can_edit, check_number
from db import User
from .context import start_registring, SEND_NUMBER_MESSAGE, MAIN_MESSAGE
import random, asyncio

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
        return await update.reply("❗️ Iltimos \"📲 Telefon raqamimni yuborish\" tugmasini bosing yoki +998951234567, 998951234567, 951234567 ko‘nishda raqamingizni yuboring.", reply_markup=KeyboardButtons.SEND_MY_NUMBER)

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
                    username=update.from_user.username,
                    phone_number=number)
        await db.register_user(user)
        if invater:
            i = await db.get_user(invater.id)
            i.invited_users += 1
            await db.update_user(i.id, invited_users = i.invited_users)
    
    await update.answer(f"{update.from_user.first_name} siz konkursimiz ishtrokchisiz!", reply_markup=KeyboardButtons.HOME)
    from handlers.admin.settings import send_saved_message
    about = context.ABOUT_LESSONS_MESSAGE
    if about.exists:
        await send_saved_message(
            chat_id=user.id,
            saved=about,
            reply_markup=InlineButtons.HOME,
            template_kwargs={'name': user.first_name}
        )
    else:
        await update.answer("❌ Xabar qo'shilmagan", reply_markup=InlineButtons.HOME)

    if invater:
        await reward_invater(i, user)



async def is_subscribed(user_id : int, chanel : str):
    try:
        member  = await bot.get_chat_member(chat_id = chanel, user_id = user_id)
        if member and member.status != 'left':
            return True
        return False  
    except Exception as e:
        return False




async def reward_invater(invater: User, user: User):
    await bot.send_message(chat_id=invater.id, text=f"{user.first_name} sizning taklif havolingiz orqali ro‘yxatdan o‘tdi!")

    if invater.invited_users == db.GIFT_POINT:
        await asyncio.sleep(3)
        await bot.send_message(chat_id=invater.id, text=random.choice(['🎉', '🥳']))
        await asyncio.sleep(2)
        await bot.send_message(chat_id=invater.id, text="🎉 Tabriklaymiz {name}! \nSiz O‘g‘iloy Xurramovaning maxsus sovg‘asini yutib olish imkoniyatni qo‘lga kiritdingiz.".format(name=invater.first_name))                               
    
    elif invater.invited_users == db.NEED_INVATE_PEOPLE:
        await asyncio.sleep(3)
        await bot.send_message(chat_id=invater.id, text=random.choice(['🎉', '🥳']))
        await asyncio.sleep(2)
        await bot.send_message(chat_id=invater.id, 
                               text="Tabriklaymiz {name} sizga bonus darslar berildi! Quydagi havola orqali bonus darslar kanaliga qo'shling 👇".format(name=invater.first_name),
                               reply_markup=InlineButtons.one_url_button("📚 Qo'shilish", db.PRIVATE_CHANNEL_URL))



@r.chat_join_request(F.chat.id == db.PRIVATE_CHANNEL_ID)
async def approve_bonus_chanel_join(request: types.ChatJoinRequest):
    user = await db.get_user(request.from_user.id)
    if user and user.invited_users >= db.NEED_INVATE_PEOPLE:
        await request.approve()
        await bot.send_message(chat_id=user.id, text= "✅ Bonus video darslar kanaliga qoshilish sorovingiz qabul qilndi",
                                   reply_markup=InlineButtons.one_url_button("Kanalga kirish", db.PRIVATE_CHANNEL_URL))
        



@r.message(StateFilter(UserStates.update_number))
async def get_number(update: types.Message, state: FSMContext):
    if update.contact:
        number = update.contact.phone_number
    
    elif update.text and check_number(update.text):
        number = update.text

    elif update.text == "⬅️ Orqaga":
        await state.clear()
        await update.reply("✅ Telefon raqamini o'zgartirish bekor qilindi", reply_markup=KeyboardButtons.HOME)
        return
    
    else:
        return await update.reply("❗️ Iltimos \"📲 Telefon raqamimni yuborish\" tugmasini bosing yoki +998951234567, 998951234567, 951234567 ko‘nishda raqamingizni yuboring.", reply_markup=KeyboardButtons.SEND_MY_NUMBER_WITH_BACK)
    
    await state.clear()
    await update.answer("✅ Telefon raqamingiz muvaffaqiyatli o'zgartirildi!", reply_markup=KeyboardButtons.HOME)
    
    user = await db.get_user(update.from_user.id)
    if user.phone_number not in number:
        await db.update_user(update.from_user.id, phone_number=number)
