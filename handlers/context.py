from states import RegisterStates
from aiogram import types
from aiogram.fsm.context import FSMContext
from buttons import InlineButtons
from loader import db, context
from db import User


SEND_NUMBER_MESSAGE = """“📲 Telefon raqamimni yuborish” tugmasini bosib telefon raqamingizni yuboring — yoki raqamingizni 951234567 kabi yozib yuborishingiz mumkin."""
WELCOME_MESSAGE = "Start xabari yuklanmagan"

MAIN_MESSAGE = """❓ Tanishlarni qanday qo’shish kerak va Ballar qanday hisoblanadi 
👥Sizga berilgan link orqali kanalga qo'shilgan do’stlaringiz uchun beriladi

+1 ball (har bir do'st uchun)

Siz {bonus} ta dostingizni taklif qilsangiz sizga “bonus darlar”     
kanali taqdim etiladi. 

Taklif qilingan dostlar soni {gift}+ bolganida sizda “maxsus sovgʻa” uchun oyin boshlanadi va jonli efirda aniqlaymiz eshigingizgacha dastafka 🚚 qilib beramiz


Faollik ko‘rsating, vazifalarni bajaring va o‘yin davomida kafolatlangan sovg‘alarni qo‘lga kiriting

Do‘stlarni taklif qilish uchun maxsus linkingizni "🔗 Maxsus havolam" tugmasini bosish orqali olishingiz mumkin.

Nechta do'stingiz qo'shilganini bilish uchun "👥 Taklif qilgan do'stlarim" tugmasini bosing"""


async def start_registring(update: types.Message, state: FSMContext, invater: User = None):
    from handlers.admin.settings import send_saved_message
    await state.set_state(RegisterStates.check_sub)
    if invater:
        await state.update_data(invater=invater)

    start = context.START_MESSAGE
    if start.exists:
        await send_saved_message(
            chat_id=update.from_user.id,
            saved=start,
            reply_markup=InlineButtons.chanels(db.chanels),
            template_kwargs={'name': update.from_user.first_name}
        )
    else:
        await update.answer(
            WELCOME_MESSAGE.format(name=update.from_user.first_name),
            reply_markup=InlineButtons.chanels(db.chanels)
        )