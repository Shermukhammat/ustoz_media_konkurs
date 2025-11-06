from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup



class KeyboardButtons:
    SEND_MY_NUMBER = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📲 Telefon raqamimni yuborish", request_contact=True)]
        ], resize_keyboard=True, one_time_keyboard=True)
    
    HOME = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔗 Maxsus havolam")],
        [KeyboardButton(text="👥 Taklif qilgan do'stlarim")]
    ], resize_keyboard=True)



