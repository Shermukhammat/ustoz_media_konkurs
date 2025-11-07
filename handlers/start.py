from loader import db, dp, bot
from aiogram import Router, types, F 
from aiogram.filters import CommandStart, CommandObject, StateFilter
from asyncio import Semaphore
from states import UserStates, RegisterStates
from aiogram.fsm.context import FSMContext
from buttons import KeyboardButtons, InlineButtons
from utils import can_edit, check_number
from db import User
from .context import start_registring, MAIN_MESSAGE, WELCOME_MESSAGE
from aiogram.fsm.state import any_state

r = Router(name='start')
dp.include_router(r)
register = Semaphore()


@r.message(CommandStart(), StateFilter(any_state))
async def command_start(update: types.Message, state: FSMContext, command: CommandObject):
    user = await db.get_user(update.from_user.id)
    if user:
        if command.args and command.args.isnumeric():
            if int(command.args) == user.id:
                await update.answer("❗️ O'zningizga ulashib bo'lmaydi")
                return
            
        await update.answer(MAIN_MESSAGE.format(name=user.first_name, bot=db.bot.full_name), reply_markup=InlineButtons.HOME)
    else:
        if command.args and command.args.isnumeric():
            invater = await db.get_user(int(command.args))
        else:
            invater = None
        await start_registring(update, state, invater = invater)



@r.callback_query(F.data == "check")
async def check(update: types.CallbackQuery, state: FSMContext):
    await delete_callback(update)
    user = await db.get_user(update.from_user.id)
    if user:
        await update.message.answer("✅ Botdan foydalanishingiz mumkin !")
    else:
        await start_registring(update.message, state)



async def delete_callback(update: types.CallbackQuery):
    if can_edit(update.message.date):
        await update.message.delete()
    else:
        await update.message.edit_reply_markup(reply_markup=None)


