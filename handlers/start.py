from loader import db, dp, bot, context
from aiogram import Router, types, F 
from aiogram.filters import CommandStart, CommandObject, StateFilter, Command
from asyncio import Semaphore
from states import UserStates, RegisterStates
from aiogram.fsm.context import FSMContext
from buttons import KeyboardButtons, InlineButtons
from utils import can_edit, check_number, sanitize_name
from db import User
from .context import start_registring, WELCOME_MESSAGE
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

        from handlers.admin.settings import send_saved_message
        start = context.SHARE_MESSAGE
        if start.exists:
            await send_saved_message(
                chat_id=update.from_user.id,
                saved=start,
                template_kwargs={'name': sanitize_name(update.from_user.first_name), 'url': f"https://t.me/{db.bot.username}?start={update.from_user.id}"}
            )
        else:
            await update.answer(
                WELCOME_MESSAGE.format(name=sanitize_name(update.from_user.first_name))
            )
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


@r.message(Command('delete_me'), StateFilter(any_state))
async def command_delete_me(update: types.Message, state: FSMContext):
    user = await db.get_user(update.from_user.id)
    if user:
        await db.remove_user(update.from_user.id)
        await state.clear()
        await update.answer(
            "🗑 Hisobingiz o'chirildi.\n"
            "Botdan qayta foydalanish uchun /start buyrug'ini yuboring."
        )
    else:
        await state.clear()
        await update.answer("❌ Siz ro'yxatdan o'tmagan siz")
