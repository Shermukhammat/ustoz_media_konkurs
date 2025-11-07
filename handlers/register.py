from loader import db, dp, bot
from aiogram import Router, types, F 
from aiogram.filters import CommandStart, CommandObject
from asyncio import Semaphore
from states import UserStates, RegisterStates
from aiogram.fsm.context import FSMContext
from buttons import KeyboardButtons, InlineButtons
from utils import can_edit, check_number
from db import User



r = Router(name='start')
dp.include_router(r)
register = Semaphore()

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




@r.callback_query(F.data == "check2")
async def check_sub(update: types.CallbackQuery, state: FSMContext):
    chanels = []
    for chanel in db.chanels:
        if not await is_subscribed(update.from_user.id, chanel.get('id')):
            chanels.append(chanel)
    
    if chanels:
        await update.answer("❗️ Iltimos kanalmizga obuna bo'ling", show_alert=True)
    else:
        await delete_callback(update)
        await update.message.answer(SEND_NUMBER_MESSAGE, reply_markup=KeyboardButtons.SEND_MY_NUMBER)
        await state.set_state(RegisterStates.get_number)

async def delete_callback(update: types.CallbackQuery):
    if can_edit(update.message.date):
        await update.message.delete()
    else:
        await update.message.edit_reply_markup(reply_markup=None)

@r.message(RegisterStates.check_sub)
async def check_message_sub(update: types.Message, state: FSMContext):
    chanels = []
    for chanel in db.chanels:
        if not await is_subscribed(update.from_user.id, chanel.get('id')):
            chanels.append(chanel)
    
    if chanels:
        await update.answer("❗️ Iltimos kanalmizga obuna bo'ling", reply_markup=InlineButtons.chanels(chanels))
    
    else:
        await update.answer(SEND_NUMBER_MESSAGE, reply_markup=KeyboardButtons.SEND_MY_NUMBER)
        await state.set_state(RegisterStates.get_number)




@r.message(RegisterStates.get_number)
async def get_number(update: types.Message, state: FSMContext):
    if update.contact:
        number = update.contact.phone_number
    
    elif update.text and check_number(update.text):
        number = update.text

    else:
        return await update.answer("❗️ Iltimos \"📲 Telefon raqamimni yuborish\" tugmasini bosing yoki +998951234567, 998951234567, 951234567 ko‘nishda raqamingizni yuboring.", reply_markup=KeyboardButtons.SEND_MY_NUMBER)

    state_data = await state.get_data()
    invater = state_data.get('invater')
    await state.clear()
    await register_user(update, invater, number)
    



async def register_user(update: types.Message, invater: User, number: str):
    async with register:
        user = await db.get_user(update.from_user.id)
        if user:
            return
        
        user = User(id = update.from_user.id, 
                    first_name=update.from_user.first_name, 
                    last_name=update.from_user.last_name, 
                    phone_number=number)
        await db.register_user(user)
        if invater:
            i = await db.get_user(invater.id)
            i.invited_users += 1
            await db.update_user(i.id, invited_users = i.invited_users)
    
    await update.answer(f"{update.from_user.first_name} siz konkursimiz ishtrokchisiz!", reply_markup=KeyboardButtons.HOME)
    await update.answer(MAIN_MESSAGE, reply_markup=InlineButtons.HOME)

    if invater:
        await bot.send_message(text = f"Sizning havolangiz orqali {update.from_user.first_name} botdan royxatdan o'tdi. Jami taklif qilgan dostlaringiz {i.invited_users} ta.",
                               chat_id = invater.id)



async def is_subscribed(user_id : int, chanel : str):
    try:
        member  = await bot.get_chat_member(chat_id = chanel, user_id = user_id)
        if member and member.status != 'left':
            return True
        return False  
    except Exception as e:
        return False
