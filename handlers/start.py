from loader import db, dp, bot
from aiogram import Router, types, F 
from aiogram.filters import CommandStart
from asyncio import Semaphore
from states import UserStates
from aiogram.fsm.context import FSMContext
from buttons import KeyboardButtons
from utils import can_edit, check_number
from db import User


r = Router(name='start')
dp.include_router(r)
register = Semaphore()
SEND_NUMER_MESSAGE = "Sizga bog'lana olishimiz uchun pastdagi “📲 Telefon raqamimni yuborish” tugmasini bosib telefon raqamingizni yuboring yoki raqamingizni 951234567 kabi yozib yuboring."


@r.message(CommandStart())
async def command_start(update: types.Message, state: FSMContext):
    user = await db.get_user(update.from_user.id)
    if user:
        await update.answer("salom")
    else:
        await state.set_state(UserStates.get_number)
        await update.answer(SEND_NUMER_MESSAGE, reply_markup=KeyboardButtons.SEND_MY_NUMBER)



@r.callback_query(F.data == "check")
async def check(update: types.CallbackQuery, state: FSMContext):
    await delete_callback(update)

    user = await db.get_user(update.from_user.id)
    if user:
        await update.message.answer("✅ Botdan foydalanishingiz mumkin !")
    else:
        await state.set_state(UserStates.get_number)
        await update.message.answer(SEND_NUMER_MESSAGE, reply_markup=KeyboardButtons.SEND_MY_NUMBER)


async def delete_callback(update: types.CallbackQuery):
    if can_edit(update.message.date):
        await update.message.delete()
    else:
        await update.message.edit_reply_markup(reply_markup=None)



@r.message(UserStates.get_number)
async def get_number(update: types.Message, state: FSMContext):
    if update.contact:
        async with register:
            user, invater = await register_user(update, update.contact.phone_number)
        
        await state.clear()
        await show_resolts(update, user, invater)

    elif len(update.text) < 20 and check_number(update.text):
        async with register:
            user, invater = await register_user(update, update.text)

        await state.clear()
        await show_resolts(update, user, invater)
        
    else:
        await update.answer(SEND_NUMER_MESSAGE, reply_markup=KeyboardButtons.SEND_MY_NUMBER)


async def show_resolts(update: types.Message, user: User, invater: User):
    if user:
        if db.welcome_message:
            await bot.copy_message(chat_id=update.from_user.id,
                                   from_chat_id=db.DATA_CHANEL_ID,
                                   message_id=db.welcome_message,
                                   reply_markup=KeyboardButtons.HOME)
        else:
            await update.answer("Assalomu alaykum {name}! {bot}ga xush kelibsiz".format(name=user.first_name, bot=db.bot.full_name),
                                reply_markup=KeyboardButtons.HOME)
        
    
    if user and invater:
        await bot.send_message(chat_id=invater.id, text="Tabriklaymiz {name} sizning taklif havolangiz orqali ro'yxatdan o'tdi".format(name=user.first_name),
                               reply_markup=KeyboardButtons.HOME)



async def register_user(update: types.Message, number: str) -> tuple[User, User]:
    user = await db.get_user(update.from_user.id)
    if user:
        return None, None
    
    user = User(id=update.from_user.id,
                first_name=update.from_user.full_name,
                username=update.from_user.username,
                phone_number=number)
    await db.register_user(user)
    pre_invate = await db.get_pre_invate(update.from_user.id)
    if not pre_invate:
        return user, None
    
    invater = await db.get_user(pre_invate.invated_user)
    if not invater:
        return user, None
    
    invater.invited_users += 1
    await db.update_user(invater.id, invited_users=invater.invited_users)
    return user, invater