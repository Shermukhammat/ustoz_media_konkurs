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
INVATE_POST_TEXT = "Konkursda qatnashish uchun quyidagi havola orqali o'ting 👇👇👇 {url}"
INVATE_CONTENT = 5

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
    msg = await bot.copy_message(chat_id=user.id,
                                 from_chat_id=db.DATA_CHANEL_ID,
                                 message_id=INVATE_CONTENT,
                                 caption=INVATE_POST_TEXT.format(url = url),
                                 reply_markup=InlineButtons.one_url_button("Ishtrok etish", url))
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
    TEXT = f"""
<b>Taklif qilingan do'stlar:</b> {invited}

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
        return "✅<b>Bonus video darslar:</b> Qo'lga kiritildi"
    return f"❗️<b>Bonus video darslar:</b> {needed} ta do'st taklif qiling."

def get_giveaway_status(needed: int) -> str:
    if needed == 0:
        return "✅<b>Maxsus sovg'a :</b> Ishtirok huquqi mavjud."
    return f"❗️<b>Maxsus sovg'a :</b>{needed}+ ta do'st taklif qiling."