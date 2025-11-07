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
import pandas as pd
from .main import r
from aiogram.enums import ContentType


@r.message(AdminPanel.get_ads_media)
async def get_ads_media(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.clear()
        await update.answer("Admin panel", reply_markup=KeyboardButtons.ADMIN_PANEL)
        return
    
    if update.content_type == ContentType.TEXT:
        await state.update_data(text = update.text)
        await state.set_state(AdminPanel.get_ads_button)
        await update.answer("Yaxshi endi tugmani yuboring (ixtyoriy). Maslan 👉  ✅ Buyerga bosing: https://t.me/mathprouz_bot?start=pro", reply_markup=KeyboardButtons.back(skip=True))

    elif update.content_type in [ContentType.PHOTO, ContentType.VIDEO, ContentType.AUDIO, ContentType.DOCUMENT, ContentType.VIDEO_NOTE, ContentType.VOICE]:
        msg = await update.copy_to(chat_id=db.DATA_CHANEL_ID)
        await state.update_data(media_id = msg.message_id, caption = update.caption, text = None)
        await state.set_state(AdminPanel.get_ads_button)
        await update.answer("Yaxshi endi tugmani yuboring (ixtyoriy). Maslan 👉  ✅ Buyerga bosing: https://t.me/mathprouz_bot?start=pro", reply_markup=KeyboardButtons.back(skip=True))

import re
url_pattern = r"^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$"
brodcast_sema = Semaphore()
from db import UserStatus

@r.message(AdminPanel.get_ads_button, F.text)
async def get_button(update: types.Message, state: FSMContext):
    state_data = await state.get_data()
    media_id = state_data.get('media_id')
    caption = state_data.get('caption')
    text = state_data.get('text')

    if update.text == "⬅️ Orqaga":
        await update.answer("Xabaringzni yuboring. (rasm, video, audio, hujjat yoki matn bo'lishi mumkin)", 
                            reply_markup=KeyboardButtons.back())
        return
        
    elif update.text == "➡️ Keyingi":
        if media_id:
            msg = await bot.copy_message(chat_id=update.from_user.id,
                                   from_chat_id=db.DATA_CHANEL_ID,
                                   message_id=media_id,
                                   caption=caption.format(name=update.from_user.first_name) if caption else None)
    
        else:
            msg = await update.answer(text.format(name=update.from_user.first_name))

        await state.set_state(AdminPanel.confirm_ads_send)
        await bot.send_message(chat_id=update.from_user.id,
                        reply_to_message_id=msg.message_id,
                        text="👆 Xabaringiz quyidagicha ko'rinadi. Agar hammasi to'g'ri bo'lsa, yuborish tugmasini bosing",
                        reply_markup=KeyboardButtons.confirm_send_ads())
        return

    if not update.entities or update.entities[0].type != 'url':
            return await update.answer("❗️ Iltimos xabaringizda tugma uchun URL manzil bo'lishi kerak!", show_alert=True)
    
    args = update.text.split(':')
    if len(args) < 2:
        await update.answer("❗️ Faqat bitta tugma bo'lishi mumkin va u quyidagi formatda bo'lishi kerak:\n\n✅ Buyerga bosing: https://t.me/mathprouz_bot?start=pro")
        return
    
    button_text = args[0].strip()
    button_url = ':'.join(args[1:]).strip()

    if not re.match(url_pattern, button_url):
        await update.reply("❗️ Xavola yaroqsiz", reply_markup=KeyboardButtons.back(skip=True))
        return
    
    if len(button_text) > 50 or len(button_text)<1:
            await update.reply("❗️ Tugma nomi 1 ta belgidan kam va 50 ta belgidan ko'p bo'lmasligi kerak", reply_markup=KeyboardButtons.back(skip=True))
            return

    await state.update_data(button_text=button_text, button_url=button_url)
    if media_id:
        msg = await bot.copy_message(chat_id=update.from_user.id,
                                   from_chat_id=db.DATA_CHANEL_ID,
                                   message_id=media_id,
                                   reply_markup=InlineButtons.one_url_button(button_text, button_url),
                                   caption=caption.format(name=update.from_user.first_name) if caption else None)
    
    else:
        msg = await update.answer(text, reply_markup=InlineButtons.one_url_button(button_text, button_url))

    await state.set_state(AdminPanel.confirm_ads_send)
    await bot.send_message(chat_id=update.from_user.id,
                           reply_to_message_id=msg.message_id,
                        text = "👆 Xabaringiz quyidagicha ko'rinadi. Agar hammasi to'g'ri bo'lsa, yuborish tugmasini bosing",
                        reply_markup=KeyboardButtons.confirm_send_ads())
    


@dp.message(AdminPanel.confirm_ads_send)
async def confirm_send(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.update_data(button_text=None, button_url=None)
        await state.set_state(AdminPanel.get_ads_button)
        await update.answer("Yaxshi endi tugmani yuboring (ixtyoriy). Maslan 👉  ✅ Buyerga bosing: https://t.me/mathprouz_bot?start=pro", 
                               reply_markup=KeyboardButtons.back(skip=True))

    elif update.text == "✅ Yuborish":
        data = await state.get_data()
        button_text = data.get('button_text')
        button_url = data.get('button_url')
        media_id = data.get('media_id')
        text = data.get('text')
        caption = data.get('caption')


        reply_markup = InlineButtons.one_url_button(button_text, button_url) if button_text else None
        await state.set_state(AdminPanel.main)
        await update.answer("Yuborilmoqda... Iltimos kuting. Bu biroz vaqt olishi mumkin.", reply_markup=KeyboardButtons.ADMIN_PANEL)
        
        async with brodcast_sema:
            await send_ads_to_users(update, text, media_id, caption, reply_markup)

    else:
        await update.answer("Xabarni yuboramizmi?", reply_markup=KeyboardButtons.confirm_send_ads())
    

from datetime import datetime
from aiogram.exceptions import TelegramForbiddenError, TelegramNotFound, TelegramRetryAfter


async def send_ads_to_users(update: types.Message, 
                            text : int = None, 
                            media_id: int = None, 
                            caption: str = None, 
                            reply_markup: types.InlineKeyboardMarkup = None):
    sended, blocked = 0, 0
    users = await db.get_useres()
    start_time = datetime.now()

    for user in users:
        if not user.is_active:
            continue
        
        status = await send_to_user(user, media_id, text, caption, reply_markup)
        if status == SendStatus.SENDED:
            sended += 1
        elif status == SendStatus.BLOCKED:
            db.update_user(user.id, status = UserStatus.blocked)
            blocked += 1
        await sleep(0.5)

    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    await update.answer(f"Xabar yuborildi!\n\n"
                        f"✅ Yuborilgan: {sended}\n"
                        f"❌ Yuborib bo'lmadi: {blocked}\n"
                        f"⏱ Umumiy vaqt: {seconds_to_hms(total_time)}")


def seconds_to_hms(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{int(hours)} soat, {int(minutes)} minut"

class SendStatus:
    SENDED = 1
    BLOCKED = -1
    ERROR = 2

async def send_to_user(user: User, media_id: int, text: str, caption: str, reply_markup: types.InlineKeyboardMarkup, attemp: int = 1, max_attempts: int = 3) -> int:
    try:
        if media_id:
            await bot.copy_message(chat_id=user.id,
                               from_chat_id=db.DATA_CHANEL_ID,
                               message_id=media_id,
                               caption=caption.format(name = user.first_name) if caption else None,
                               reply_markup=reply_markup)
        else:
            await bot.send_message(chat_id=user.id, text=text.format(name=user.first_name), reply_markup=reply_markup)

        return SendStatus.SENDED
    
    except TelegramRetryAfter as e:
        await sleep(e.retry_after+10)
        if attemp > max_attempts:
            return SendStatus.ERROR
        return await send_to_user(user, media_id, text, caption, reply_markup, attemp=attemp+1, max_attempts=max_attempts)

    except TelegramForbiddenError:
        return SendStatus.BLOCKED

    except Exception as e:
        return SendStatus.ERROR