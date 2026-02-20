from loader import db, dp, bot, context
from aiogram import types, F
from aiogram.enums import ContentType
from aiogram.utils.text_decorations import html_decoration
from states import AdminPanel
from aiogram.fsm.context import FSMContext
from buttons import KeyboardButtons, InlineButtons
from .main import r


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _extract_message_data(update: types.Message) -> dict:
    """Extract all fields needed to re-send a message later, with template-safe text/caption."""
    ct = update.content_type

    # For text messages: store the HTML-rendered text (preserves bold/links etc.)
    if ct == ContentType.TEXT:
        text = update.html_text if update.entities else update.text
        return {
            'content_type': 'text',
            'file_id': None,
            'text': text,
            'caption': None,
            'parse_mode': 'HTML' if update.entities else None,
        }

    # For media: get the file_id from the right attribute
    file_id = None
    if ct == ContentType.PHOTO:
        file_id = update.photo[-1].file_id
    elif ct == ContentType.VIDEO:
        file_id = update.video.file_id
    elif ct == ContentType.DOCUMENT:
        file_id = update.document.file_id
    elif ct == ContentType.VOICE:
        file_id = update.voice.file_id
    elif ct == ContentType.VIDEO_NOTE:
        file_id = update.video_note.file_id
    elif ct == ContentType.AUDIO:
        file_id = update.audio.file_id

    if update.caption_entities:
        caption = html_decoration.unparse(update.caption or '', update.caption_entities)
    else:
        caption = update.caption

    return {
        'content_type': ct.value,   # store plain string, not enum
        'file_id': file_id,
        'text': None,
        'caption': caption,
        'parse_mode': 'HTML' if update.caption_entities else None,
    }


async def send_saved_message(chat_id: int,
                             saved,
                             reply_markup=None,
                             template_kwargs: dict = None) -> types.Message:
    """Re-send a SavedMessage to chat_id, applying optional template substitutions."""
    ct = saved.content_type
    pm = saved.parse_mode

    def fmt(s):
        if s and template_kwargs:
            return s.format(**template_kwargs)
        return s

    if ct == 'text':
        return await bot.send_message(chat_id=chat_id,
                                      text=fmt(saved.text),
                                      parse_mode=pm,
                                      reply_markup=reply_markup)

    cap = fmt(saved.caption)
    fid = saved.file_id

    if ct == ContentType.PHOTO:
        return await bot.send_photo(chat_id=chat_id, photo=fid, caption=cap, parse_mode=pm, reply_markup=reply_markup)
    elif ct == ContentType.VIDEO:
        return await bot.send_video(chat_id=chat_id, video=fid, caption=cap, parse_mode=pm, reply_markup=reply_markup)
    elif ct == ContentType.DOCUMENT:
        return await bot.send_document(chat_id=chat_id, document=fid, caption=cap, parse_mode=pm, reply_markup=reply_markup)
    elif ct == ContentType.VOICE:
        return await bot.send_voice(chat_id=chat_id, voice=fid, caption=cap, parse_mode=pm, reply_markup=reply_markup)
    elif ct == ContentType.VIDEO_NOTE:
        return await bot.send_video_note(chat_id=chat_id, video_note=fid, reply_markup=reply_markup)
    elif ct == ContentType.AUDIO:
        return await bot.send_audio(chat_id=chat_id, audio=fid, caption=cap, parse_mode=pm, reply_markup=reply_markup)

    raise ValueError(f"Unsupported content_type: {ct}")


# ─── Show current share message ───────────────────────────────────────────────

@r.message(AdminPanel.settings, F.text == "🔗 Taklif havolam xabari")
async def show_share_message(update: types.Message, state: FSMContext):
    share = context.SHARE_MESSAGE

    if share.exists:
        await send_saved_message(
                chat_id=update.from_user.id,
                saved=share,
                reply_markup=InlineButtons.CHANGE_SHARE_MESSAGE,
                template_kwargs={}
            )
    
    else:
        await update.answer(
            "❌ Taklif havolasi xabari qo'shilmagan.",
            reply_markup=InlineButtons.CHANGE_SHARE_MESSAGE
        )


# ─── "Change" inline button ───────────────────────────────────────────────────

@r.callback_query(AdminPanel.settings, F.data == 'change_share_message')
async def change_share_message_callback(update: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminPanel.set_share_message)
    await update.answer()
    await update.message.answer(
        "📨 Yangi xabarni yuboring.\n"
        "Rasm, video, matn yoki boshqa turdagi xabar bo'lishi mumkin.\n\n"
        "💡 Havola uchun <code>{url}</code>, foydalanuvchi ismi uchun <code>{name}</code> yozing.",
        parse_mode='HTML',
        reply_markup=KeyboardButtons.back()
    )


# ─── Receive new share message ────────────────────────────────────────────────

SUPPORTED_TYPES = {
    ContentType.TEXT, ContentType.PHOTO, ContentType.VIDEO,
    ContentType.DOCUMENT, ContentType.VOICE, ContentType.VIDEO_NOTE,
    ContentType.AUDIO,
}

@r.message(AdminPanel.set_share_message)
async def set_share_message_handler(update: types.Message, state: FSMContext):
    # Back button
    if update.content_type == ContentType.TEXT and update.text == "⬅️ Orqaga":
        await state.set_state(AdminPanel.settings)
        await update.answer("Sozlamalar bo'limi", reply_markup=KeyboardButtons.SETTINGS)
        return

    if update.content_type not in SUPPORTED_TYPES:
        await update.answer(
            "❗️ Ushbu turdagi xabar qo'llab-quvvatlanmaydi.\n"
            "Rasm, video, matn, hujjat, ovozli xabar yoki doiraviy video yuboring.",
            reply_markup=KeyboardButtons.back()
        )
        return

    try:
        from db.params import SavedMessage
        data = _extract_message_data(update)
        saved = SavedMessage(data)
        await context.update_save_message('share_message', saved)
        context.SHARE_MESSAGE = saved          # update in-memory reference
        await state.set_state(AdminPanel.settings)
        await update.answer(
            "✅ Taklif havolam xabari saqlandi!",
            reply_markup=KeyboardButtons.SETTINGS
        )
    except Exception as e:
        await update.answer(
            f"❗️ Xatolik yuz berdi: {e}",
            reply_markup=KeyboardButtons.back()
        )


# ─── Show current "Bepul darslar" message ─────────────────────────────────────

@r.message(AdminPanel.settings, F.text == "📕 Bepul darslar xabari")
async def show_about_lessons_message(update: types.Message, state: FSMContext):
    msg = context.ABOUT_LESSONS_MESSAGE

    if msg.exists:
        await send_saved_message(
            chat_id=update.from_user.id,
            saved=msg,
            reply_markup=InlineButtons.CHANGE_ABOUT_LESSONS_MESSAGE,
            template_kwargs={}
        )
    else:
        await update.answer(
            "❌ Bepul darslar xabari qo'shilmagan.",
            reply_markup=InlineButtons.CHANGE_ABOUT_LESSONS_MESSAGE
        )


# ─── "Change" inline button ───────────────────────────────────────────────────

@r.callback_query(AdminPanel.settings, F.data == 'change_about_lessons_message')
async def change_about_lessons_message_callback(update: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminPanel.set_about_lessons_message)
    await update.answer()
    await update.message.answer(
        "📨 Yangi xabarni yuboring.\n"
        "Rasm, video, matn yoki boshqa turdagi xabar bo'lishi mumkin.\n\n"
        "💡 Foydalanuvchi ismi uchun <code>{name}</code> yozing.",
        parse_mode='HTML',
        reply_markup=KeyboardButtons.back()
    )


# ─── Receive new "Bepul darslar" message ──────────────────────────────────────

@r.message(AdminPanel.set_about_lessons_message)
async def set_about_lessons_message_handler(update: types.Message, state: FSMContext):
    if update.content_type == ContentType.TEXT and update.text == "⬅️ Orqaga":
        await state.set_state(AdminPanel.settings)
        await update.answer("Sozlamalar bo'limi", reply_markup=KeyboardButtons.SETTINGS)
        return

    if update.content_type not in SUPPORTED_TYPES:
        await update.answer(
            "❗️ Ushbu turdagi xabar qo'llab-quvvatlanmaydi.\n"
            "Rasm, video, matn, hujjat, ovozli xabar yoki doiraviy video yuboring.",
            reply_markup=KeyboardButtons.back()
        )
        return

    try:
        from db.params import SavedMessage
        data = _extract_message_data(update)
        saved = SavedMessage(data)
        await context.update_save_message('about_lessons_message', saved)
        context.ABOUT_LESSONS_MESSAGE = saved      # update in-memory reference
        await state.set_state(AdminPanel.settings)
        await update.answer(
            "✅ Bepul darslar xabari saqlandi!",
            reply_markup=KeyboardButtons.SETTINGS
        )
    except Exception as e:
        await update.answer(
            f"❗️ Xatolik yuz berdi: {e}",
            reply_markup=KeyboardButtons.back()
        )


# ─── Show current "Start" message ─────────────────────────────────────────────

@r.message(AdminPanel.settings, F.text == "🏃 Start xabari")
async def show_start_message(update: types.Message, state: FSMContext):
    msg = context.START_MESSAGE

    if msg.exists:
        await send_saved_message(
            chat_id=update.from_user.id,
            saved=msg,
            reply_markup=InlineButtons.CHANGE_START_MESSAGE,
            template_kwargs={'name': update.from_user.first_name}
        )
    else:
        await update.answer(
            "❌ Start xabari qo'shilmagan.",
            reply_markup=InlineButtons.CHANGE_START_MESSAGE
        )


# ─── "Change" inline button ───────────────────────────────────────────────────

@r.callback_query(AdminPanel.settings, F.data == 'change_start_message')
async def change_start_message_callback(update: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminPanel.set_start_message)
    await update.answer()
    await update.message.answer(
        "📨 Yangi start xabarni yuboring.\n"
        "Rasm, video, matn yoki boshqa turdagi xabar bo'lishi mumkin.\n\n"
        "💡 Foydalanuvchi ismi uchun <code>{name}</code> yozing.",
        parse_mode='HTML',
        reply_markup=KeyboardButtons.back()
    )


# ─── Receive new "Start" message ──────────────────────────────────────────────

@r.message(AdminPanel.set_start_message)
async def set_start_message_handler(update: types.Message, state: FSMContext):
    if update.content_type == ContentType.TEXT and update.text == "⬅️ Orqaga":
        await state.set_state(AdminPanel.settings)
        await update.answer("Sozlamalar bo'limi", reply_markup=KeyboardButtons.SETTINGS)
        return

    if update.content_type not in SUPPORTED_TYPES:
        await update.answer(
            "❗️ Ushbu turdagi xabar qo'llab-quvvatlanmaydi.\n"
            "Rasm, video, matn, hujjat, ovozli xabar yoki doiraviy video yuboring.",
            reply_markup=KeyboardButtons.back()
        )
        return

    try:
        from db.params import SavedMessage
        data = _extract_message_data(update)
        saved = SavedMessage(data)
        await context.update_save_message('start_message', saved)
        context.START_MESSAGE = saved      # update in-memory reference
        await state.set_state(AdminPanel.settings)
        await update.answer(
            "✅ Start xabari saqlandi!",
            reply_markup=KeyboardButtons.SETTINGS
        )
    except Exception as e:
        await update.answer(
            f"❗️ Xatolik yuz berdi: {e}",
            reply_markup=KeyboardButtons.back()
        )


# ─── Show private channel info ────────────────────────────────────────────────

@r.message(AdminPanel.settings, F.text == "🔐 Yopiq kanal")
async def show_private_channel(update: types.Message, state: FSMContext):
    ch_id = db.PRIVATE_CHANNEL_ID
    ch_url = db.PRIVATE_CHANNEL_URL

    if ch_id:
        text = (
            f"🔐 <b>Yopiq kanal ma'lumotlari:</b>\n\n"
            f"🆔 ID: <code>{ch_id}</code>\n"
        )
        if ch_url:
            text += f"🔗 Havola: {ch_url}"
        else:
            text += "🔗 Havola: <i>mavjud emas</i>"
    else:
        text = "❌ Yopiq kanal qo'shilmagan."

    await update.answer(
        text,
        parse_mode='HTML',
        reply_markup=InlineButtons.CHANGE_PRIVATE_CHANNEL
    )


# ─── "Change channel" inline callback ─────────────────────────────────────────

@r.callback_query(AdminPanel.settings, F.data == 'change_private_channel')
async def change_private_channel_callback(update: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminPanel.set_private_channel)
    await update.answer()
    await update.message.answer(
        "📡 Yangi yopiq kanal ID sini yuboring.\n\n"
        "Bot o'sha kanalga <b>admin</b> bo'lishi kerak.\n"
        "Kanal ID odatda manfiy son ko'rinishida bo'ladi, masalan: <code>-1001234567890</code>",
        parse_mode='HTML',
        reply_markup=KeyboardButtons.back()
    )


# ─── Receive new private channel ID ───────────────────────────────────────────

@r.message(AdminPanel.set_private_channel)
async def set_private_channel_handler(update: types.Message, state: FSMContext):
    # Back button
    if update.content_type == ContentType.TEXT and update.text == "⬅️ Orqaga":
        await state.set_state(AdminPanel.settings)
        await update.answer("Sozlamalar bo'limi", reply_markup=KeyboardButtons.SETTINGS)
        return

    if update.content_type != ContentType.TEXT:
        await update.answer(
            "❗️ Iltimos, kanal ID sini raqam ko'rinishida yuboring.",
            reply_markup=KeyboardButtons.back()
        )
        return

    raw = update.text.strip()
    try:
        channel_id = int(raw)
    except ValueError:
        await update.answer(
            "❗️ Noto'g'ri format. Kanal ID raqam bo'lishi kerak, "
            "masalan: <code>-1001234567890</code>",
            parse_mode='HTML',
            reply_markup=KeyboardButtons.back()
        )
        return

    try:
        chat = await bot.get_chat(channel_id)
        bot_member = await bot.get_chat_member(channel_id, (await bot.me()).id)

        if bot_member.status not in ('administrator', 'creator'):
            await update.answer(
                "❗️ Bot ushbu kanalda admin emas. "
                "Botni kanalga admin qilib qo'shing va qayta urinib ko'ring.",
                reply_markup=KeyboardButtons.back()
            )
            return

        # Create a join-request invite link
        invite = await bot.create_chat_invite_link(
            channel_id,
            creates_join_request=True
        )
        invite_url = invite.invite_link

        await db.update_private_channel(channel_id, invite_url)

        await state.set_state(AdminPanel.settings)
        await update.answer(
            f"✅ Yopiq kanal muvaffaqiyatli saqlandi!\n\n"
            f"🆔 ID: <code>{channel_id}</code>\n"
            f"🔗 Havola: {invite_url}",
            parse_mode='HTML',
            reply_markup=KeyboardButtons.SETTINGS
        )

    except Exception as e:
        await update.answer(
            f"❗️ Xatolik yuz berdi: kanal topilmadi yoki bot unga kirish huquqiga ega emas.\n"
            f"<i>{e}</i>",
            parse_mode='HTML',
            reply_markup=KeyboardButtons.back()
        )


# ─── Show "Need Invite People" info ───────────────────────────────────────────

@r.message(AdminPanel.settings, F.text == "🔢 Odam qo'shish soni")
async def show_need_invite_people(update: types.Message, state: FSMContext):
    count = db.NEED_INVATE_PEOPLE
    
    await update.answer(
        f"🔢 <b>Odam qo'shish soni:</b> {count} ta\n\n"
        "Foydalanuvchi konkursda qatnashishi uchun shuncha odam qo'shishi kerak.",
        parse_mode='HTML',
        reply_markup=InlineButtons.CHANGE_NEED_INVITE_PEOPLE
    )


# ─── "Change need invite people" inline callback ──────────────────────────────

@r.callback_query(AdminPanel.settings, F.data == 'change_need_invite_people')
async def change_need_invite_people_callback(update: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminPanel.set_need_invite_people)
    await update.answer()
    await update.message.answer(
        "🔢 Yangi qiymatni yuboring.\n"
        "Bu foydalanuvchi konkursda qatnashishi uchun qo'shishi kerak bo'lgan odamlar soni.\n"
        "Qiymat <b>1 dan 100 gacha</b> bo'lishi kerak.",
        parse_mode='HTML',
        reply_markup=KeyboardButtons.back()
    )


# ─── Receive new "Need Invite People" value ───────────────────────────────────

@r.message(AdminPanel.set_need_invite_people)
async def set_need_invite_people_handler(update: types.Message, state: FSMContext):
    # Back button
    if update.content_type == ContentType.TEXT and update.text == "⬅️ Orqaga":
        await state.set_state(AdminPanel.settings)
        await update.answer("Sozlamalar bo'limi", reply_markup=KeyboardButtons.SETTINGS)
        return

    if update.content_type != ContentType.TEXT:
        await update.answer(
            "❗️ Noto'g'ri format. Raqam kiriting.",
            reply_markup=KeyboardButtons.back()
        )
        return

    raw = update.text.strip()
    if not raw.isdigit():
        await update.answer(
            "❗️ Noto'g'ri format. Raqam kiriting.",
            reply_markup=KeyboardButtons.back()
        )
        return

    val = int(raw)
    if not (1 <= val <= 100):
        await update.answer(
            "❗️ Iltimos, 1 dan 100 gacha bo'lgan raqam kiriting.",
            reply_markup=KeyboardButtons.back()
        )
        return

    await db.update_need_invite_people(val)
    
    await state.set_state(AdminPanel.settings)
    await update.answer(
        f"✅ Saqlandi!\n\n"
        f"🔢 Odam qo'shish soni: {val} ta",
        parse_mode='HTML',
        reply_markup=KeyboardButtons.SETTINGS
    )


# ─── Settings: Back to admin panel & catch-all ────────────────────────────────

@r.message(AdminPanel.settings, F.text == "⬅️ Orqaga")
async def settings_back(update: types.Message, state: FSMContext):
    await state.set_state(AdminPanel.main)
    await update.answer("Admin panel", reply_markup=KeyboardButtons.ADMIN_PANEL)


@r.message(AdminPanel.settings)
async def settings_catchall(update: types.Message, state: FSMContext):
    await update.answer("Sozlamalar bo'limi", reply_markup=KeyboardButtons.SETTINGS)
