from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup



class KeyboardButtons:
    SEND_MY_NUMBER = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📲 Telefon raqamimni yuborish", request_contact=True)]
        ], resize_keyboard=True, one_time_keyboard=True)
    
    SEND_MY_NUMBER_WITH_BACK = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📲 Telefon raqamimni yuborish", request_contact=True)],
        [KeyboardButton(text="⬅️ Orqaga")]
        ], resize_keyboard=True, one_time_keyboard=True)
    
    HOME = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔗 Maxsus havolam"), KeyboardButton(text="👥 Taklif qilgan do'stlarim")],
        [KeyboardButton(text="📱 Telefon raqamim"), KeyboardButton(text="📖 Yordam")]
    ], resize_keyboard=True)

    ADMIN_PANEL = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="⬇️ Foydlanuvchilar excel jadvali"), KeyboardButton(text="🚀 Xabar yuborish")],
        [KeyboardButton(text="👨🏻‍💻 Adminlar"), KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="⬅️ Chiqish")]
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

    def one_url_button(name: str, url: str):
        return InlineKeyboardMarkup(inline_keyboard=[
                                   [InlineKeyboardButton(text=name, url=url)]
                                ])

    def one_callback_button(name: str, data: str):
        return InlineKeyboardMarkup(inline_keyboard=[
                                   [InlineKeyboardButton(text=name, callback_data=data)]
                                ])