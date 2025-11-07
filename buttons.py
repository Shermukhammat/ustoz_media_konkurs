from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup



class KeyboardButtons:
    SEND_MY_NUMBER = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📲 Telefon raqamimni yuborish", request_contact=True)]
        ], resize_keyboard=True, one_time_keyboard=True)
    
    HOME = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔗 Maxsus havolam")],
        [KeyboardButton(text="👥 Taklif qilgan do'stlarim")]
    ], resize_keyboard=True)



class InlineButtons:
    HOME = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Maxsus havolam", callback_data="url")]
    ])

    @staticmethod
    def chanels(chanels: list[dict]) -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text=chanel.get('name', 'Kanal'), url=chanel.get('url'))]
            for chanel in chanels
        ]
        buttons.append([InlineKeyboardButton(text="✅ А'zo boʼldim", callback_data="check2")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)


