from states import RegisterStates
from aiogram import types
from aiogram.fsm.context import FSMContext
from buttons import InlineButtons
from loader import db 
from db import User


SEND_NUMBER_MESSAGE = """
🎉 Konkursimzda ishtirok etayotganingizdan xursandmiz!
Siz bilan bog‘lanishimiz uchun quyidagi “📲 Telefon raqamimni yuborish” tugmasini bosib telefon raqamingizni yuboring — yoki raqamingizni 951234567 kabi yozib yuborishingiz mumkin.
Sovg‘angizni yetkazib berish uchun telefon raqamingiz zarur. Biz siz bilan bog‘lanib, sovg‘angizni to‘g‘ridan-to‘g‘ri eshigingizgacha yetkazib beramiz 🚚✨
"""


WELCOME_MESSAGE = """Assalomu alaykum {name}! O‘g‘loy Khurramovaning konkurs botiga xush kelibsiz! 🎉 
Konkursga qatnashish uchun pastda so’ralgan ma’lumotlarni yuboring va aytilgan amallarni bajaring.

Qani kettik!!!

Birinchi navbatda kanalimzga qo'shiling va ✅ А'zo boʼldim tugmasini bosing"""

MAIN_MESSAGE = """❓ Tanishlarni qanday qo’shish kerak va Ballar qanday hisoblanadi 
👥Sizga berilgan link orqali kanalga qo'shilgan do’stlaringiz uchun beriladi

+1 ball (har bir do'st uchun)

Siz 10 ta dostingizni taklif qilsangiz sizga “bonus darlar”     
kanali taqdim etiladi. 

Taklif qilingan dostlar soni 10+ bolganida sizda “maxsus sovgʻa” uchun oyin boshlanadi va jonli efirda aniqlaymiz eshigingizgacha dastafka 🚚 qilib beramiz


Faollik ko‘rsating, vazifalarni bajaring va o‘yin davomida kafolatlangan sovg‘alarni qo‘lga kiriting

Do‘stlarni taklif qilish uchun maxsus linkingizni "Mening shaxsiy linkim 🔗" tugmasini bosish orqali olishingiz mumkin.

Nechta do'stingiz qo'shilganini bilish uchun "Mening hisobim 📑" tugmasini bosing"""



async def start_registring(update: types.Message, state: FSMContext, invater : User = None):
    await state.set_state(RegisterStates.check_sub)
    if invater:
        await state.update_data(invater = invater)
    
    await update.answer(WELCOME_MESSAGE.format(name=update.from_user.first_name), 
                        reply_markup=InlineButtons.chanels(db.chanels))