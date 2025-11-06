from loader import db, dp, bot
from aiogram import Router, types, F 
from aiogram.filters import CommandStart, CommandObject
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
async def command_start(update: types.Message, state: FSMContext, command: CommandObject):
    user = await db.get_user(update.from_user.id)
    if user:
        if command.args and command.args.isnumeric():
            if int(command.args) == user.id:
                await update.answer("❗️ O'zningizga ulashib bo'lmaydi")
                return
            
        await update.answer("salom")
    else:
        await register_user(update)



@r.callback_query(F.data == "check")
async def check(update: types.CallbackQuery, state: FSMContext):
    await delete_callback(update)
    user = await db.get_user(update.from_user.id)
    if user:
        await update.message.answer("✅ Botdan foydalanishingiz mumkin !")
    else:
        await register_user(update.message)


async def delete_callback(update: types.CallbackQuery):
    if can_edit(update.message.date):
        await update.message.delete()
    else:
        await update.message.edit_reply_markup(reply_markup=None)



async def register_user(update: types.Message):
    async with register:
        user, invater = await register_user_to_db(update)
    await show_resolts(update, user, invater)


async def show_resolts(update: types.Message, user: User, invater: User):
    if user:
        WELCOME_MESSAGE = "Assalomu alaykum {name}! {bot} bot ga xush kelibsiz. Siz 15 ta tanishingizni taklif qilsangiz bonus darsga ega bolasiz"
        await update.answer(WELCOME_MESSAGE.format(name=user.first_name, bot=db.bot.full_name),
                            reply_markup=KeyboardButtons.HOME)
        
    
    if user and invater:
        await bot.send_message(chat_id=invater.id, text="Tabriklaymiz {name} sizning taklif havolangiz orqali ro'yxatdan o'tdi".format(name=user.first_name),
                               reply_markup=KeyboardButtons.HOME)



async def register_user_to_db(update: types.Message) -> tuple[User, User]:
    user = await db.get_user(update.from_user.id)
    if user:
        return None, None
    
    user = User(id=update.from_user.id,
                first_name=update.from_user.full_name,
                username=update.from_user.username)
    await db.register_user(user)
    pre_invate = await db.get_pre_invate(update.from_user.id)
    await db.remove_pre_invate(update.from_user.id)
    if not pre_invate:
        return user, None
    
    invater = await db.get_user(pre_invate.invated_user)
    if not invater:
        return user, None

    invater.invited_users += 1
    await db.update_user(invater.id, invited_users=invater.invited_users)
    return user, invater