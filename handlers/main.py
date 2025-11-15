from loader import db, dp, bot
from aiogram import Router, types, F 
from aiogram.filters import CommandStart
from asyncio import Semaphore
from states import UserStates
from aiogram.fsm.context import FSMContext
from buttons import KeyboardButtons, InlineButtons
from utils import can_edit, check_number
from .context import start_registring, MAIN_MESSAGE
from db import User


r = Router(name='main')
dp.include_router(r)
register = Semaphore()
INVATE_POST_TEXT = "Bonus darslar va Sovgʻalarni yutib olish uchun sizning maxsus xavolangiz 👇👇👇 \n{url}"
INVATE_CONTENT = 9

@r.message(F.text)
async def main_message(update: types.Message, state: FSMContext):
    user = await db.get_user(update.from_user.id)
    if not user:
        return await start_registring(update, state)
    
    if update.text == "👥 Taklif qilgan do'stlarim":
        await show_points(update, user)
    
    elif update.text == "🔗 Maxsus havolam":
        await send_invate_post(update, user)

    elif update.text == "📖 Yordam":
        await update.answer(MAIN_MESSAGE.format(name=user.first_name, bot=db.bot.full_name, bonus=db.BONUS_POINT, gift=db.GIFT_POINT), reply_markup=InlineButtons.HOME)   
    
    elif update.text == "📱 Telefon raqamim":
        await update.answer(
    "❗️Bu raqam faqat g‘olib bo‘lganingizda siz bilan bog‘lanish uchun ishlatiladi.\n"
    "Iltimos, raqam to‘g‘riligini tekshiring.\n\n"
    f"<b>Raqam:</b> {user.phone_number}",
    reply_markup=InlineButtons.one_callback_button("✏️ O‘zgartirish", "update_number"),
    parse_mode="HTML"
)
     
    else:
        await update.answer("👇 Iltimos quyidagi tugmalardan birni bosing.", reply_markup=KeyboardButtons.HOME)


@r.callback_query(F.data == "url")
async def url(update: types.CallbackQuery, state: FSMContext):
    user = await db.get_user(update.from_user.id)
    if user:
        await send_invate_post(update.message, user)


async def send_invate_post(update: types.Message, user: User):
    url = f"https://t.me/{db.bot.username}?start={user.id}"
    switcher = types.SwitchInlineQueryChosenChat(query=f'invite_{user.id}', 
                                                 allow_user_chats=True, 
                                                 allow_group_chats=True,
                                                 allow_channel_chats=True)
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
                                     [types.InlineKeyboardButton(text="↪️ Ulashish", switch_inline_query_chosen_chat=switcher)]
                                     ])
    msg = await bot.copy_message(chat_id=user.id,
                                 from_chat_id=db.DATA_CHANEL_ID,
                                 message_id=INVATE_CONTENT,
                                 caption=INVATE_POST_TEXT.format(url = url),
                                 reply_markup=markup)
    await bot.send_message(chat_id=user.id,
                           reply_to_message_id=msg.message_id,
                           reply_markup=KeyboardButtons.HOME,
                           text="👆👆👆 Bu postda sizning shaxsiy linkingiz joylashgan \n\nYuqoridagi postni yaqinlaringizga tarqating, ular sizning linkingizni bosib botga start berishi va telegram kanalga obuna bo’lishi kerak.")



@r.callback_query(F.data == "update_number")
async def update_number(update: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.update_number)
    await update.answer("⏳")
    await update.message.answer("❗️ Iltimos \"📲 Telefon raqamimni yuborish\" tugmasini bosing yoki +998951234567, 998951234567, 951234567 ko‘nishda raqamingizni yuboring.", reply_markup=KeyboardButtons.SEND_MY_NUMBER_WITH_BACK)


async def show_points(update: types.Message, user: User):
    invited = user.invited_users
    bonus_needed = max(0, db.BONUS_POINT - invited)
    gift_needed = max(0, db.GIFT_POINT - invited)
    markup = InlineButtons.one_url_button('📚 Bonus video darslar', db.BONUS_CHANEL_URL) if db.BONUS_POINT <= user.invited_users else KeyboardButtons.HOME
    TEXT = f"""Taklif qilingan do'stlaringiz soni {invited} ta

{get_bonus_video_status(bonus_needed)}
{get_giveaway_status(gift_needed)}
"""
    await update.answer(
        TEXT.strip(),
        reply_markup=markup,
        parse_mode="HTML",
    )

def get_bonus_video_status(needed: int) -> str:
    if needed == 0:
        return "✅ <b>Bonus darslar qo'lga kiritildi!</b>"
    return f"❗️<b>Bonus darslarni qo'lga kiritish uchun {needed} ta odam taklif qilining.</b>"

def get_giveaway_status(needed: int) -> str:
    if needed == 0:
        return "✅ <b>Maxsus sovg‘a yutish imkoniyati sizda mavjud!</b>"
    return f"❗️<b>Maxsus sovg‘ani yutish imkoniyatini qo‘lga kiritish uchun {needed}+ ta odam taklif qilining.</b>"



from uuid import uuid4

@dp.inline_query()
async def inline_invite_handler(inline_query: types.InlineQuery):
    inviter_id = inline_query.from_user.id
    url = f"https://t.me/{db.bot.username}?start={inviter_id}"
    caption = "O‘gloy Khurramovaning bonus darslari va sovg‘alarni yutib olish uchun pastdagi tugmani bosing 👇👇👇"
    photo_file_id = 'AgACAgIAAyEFAATCO-qgAAMJaRhoUn0B1ExH950SaTNiaq1oeyMAAg0OaxuurcFIgXxeXIejbacBAAMCAAN4AAM2BA'
    photo_url = "https://odilovfarrux.uz/media/admin_uploaded_files/ustoz_media.jpg"
    result = types.InlineQueryResultArticle(
    id=uuid4().hex,
    title="↪️ Havolani ulashish uchun bosing",
    thumbnail_url = photo_url,
    input_message_content=types.InputTextMessageContent(message_text=caption, parse_mode='HTML'),
    reply_markup=InlineButtons.one_url_button("Ishtrok etish", url)
    )

    await inline_query.answer(
        results=[result],
        cache_time=60,
        is_personal=True,
    )


@dp.channel_post(F.photo)
async def show_id(update: types.Message):
    print(update.photo[-1].file_id)