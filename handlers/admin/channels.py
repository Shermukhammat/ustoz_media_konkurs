from loader import db, dp, bot
from aiogram import Router, types, F 
from aiogram.filters import Command
from asyncio import Semaphore
from states import AdminPanel
from aiogram.fsm.context import FSMContext
from buttons import KeyboardButtons, InlineButtons
from utils import can_edit
from db import User
from asyncio import sleep

r = Router(name='admin_channels')
dp.include_router(r)


@r.message(AdminPanel.main, F.text == "📡 Kanallar")
async def admin_channels_list(update: types.Message, state: FSMContext):
    text = "📑 Kanallar ro'yxati: \n"
    if not db.chanels:
        text += "Hozircha kanallar yo'q."
    else:
        for index, channel in enumerate(db.chanels):
            text += f"\n{index+1}. {channel.get('name', 'Nomsiz')} \n🆔: <code>{channel.get('id')}</code>\n🔗: {channel.get('url', 'Havola yo`q')}\n"
    
    await update.answer(text, parse_mode='HTML', reply_markup=InlineButtons.CHANNELS_BUTTON)


@r.callback_query(F.data == 'add_channel')
async def add_channel_callback(update: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminPanel.add_channel)
    await update.message.answer("Kanal ID sini yoki username sini yuboring (bot shu kanalda admin bo'lishi shart).\nMasalan: -100123456789 yoki @kanal_username",
                        reply_markup=KeyboardButtons.back())

@r.callback_query(F.data == 'remove_channel')
async def remove_channel_callback(update: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminPanel.remove_channel)
    await update.message.answer("O'chirmoqchi bo'lgan kanal ID sini yuboring.",
                        reply_markup=KeyboardButtons.back())


@r.message(AdminPanel.add_channel, F.text)
async def add_channel_handler(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.set_state(AdminPanel.main)
        await update.answer("Admin panel", reply_markup=KeyboardButtons.ADMIN_PANEL)
        return

    channel_input = update.text
    try:
        # Check if input is ID or username
        if channel_input.lstrip('-').isdigit():
            chat_id = int(channel_input)
        else:
            chat_id = channel_input

        # Get chat info to verify admin status and get details
        chat = await bot.get_chat(chat_id)
        
        # Check if bot is admin
        member = await bot.get_chat_member(chat.id, bot.id)
        if not member.status in ['administrator', 'creator']:
             await update.reply("❗️ Bot ushbu kanalda admin emas. Iltimos avval botni admin qiling.", reply_markup=KeyboardButtons.back())
             return

        # Check if channel already exists
        if any(c.get('id') == chat.id for c in db.chanels):
            await update.reply("❗️ Ushbu kanal allaqochon qo'shilgan.", reply_markup=KeyboardButtons.back())
            return

        # Create invite link
        invite_link = await bot.create_chat_invite_link(
            chat_id=chat.id,
            name="Bot Invite Link"
        )

        channel_data = {
            'id': chat.id,
            'name': chat.title,
            'username': chat.username,
            'url': invite_link.invite_link
        }

        await db.add_channel(channel_data)
        
        await state.set_state(AdminPanel.main)
        await update.answer(f"✅ Kanal muvaffaqiyatli qo'shildi:\n<b>{chat.title}</b>\nHavola: {invite_link.invite_link}", 
                            parse_mode='HTML',
                            reply_markup=KeyboardButtons.ADMIN_PANEL)

    except Exception as e:
        await update.reply(f"❗️ Xatolik yuz berdi: {str(e)}\nIltimos ID yoki usernameni to'g'ri kiriting va bot admin ekanligini tekshiring.", reply_markup=KeyboardButtons.back())


@r.message(AdminPanel.remove_channel, F.text)
async def remove_channel_handler(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.set_state(AdminPanel.main)
        await update.answer("Admin panel", reply_markup=KeyboardButtons.ADMIN_PANEL)
        return

    if update.text.lstrip('-').isdigit():
        channel_id = int(update.text)
        
        # Check if channel exists
        channel = next((c for c in db.chanels if c.get('id') == channel_id), None)
        if channel:
            await db.remove_channel(channel_id)
            await state.set_state(AdminPanel.main)
            await update.answer("✅ Kanal o'chirildi", reply_markup=KeyboardButtons.ADMIN_PANEL)
        else:
            await update.reply("❗️ Bunday ID li kanal topilmadi", reply_markup=KeyboardButtons.back())
    else:
        await update.reply("❗️ Iltimos ID ni to'g'ri kiriting (faqat raqamlar)", reply_markup=KeyboardButtons.back())
