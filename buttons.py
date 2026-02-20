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
        [KeyboardButton(text="🔗 Taklif havolam")],
        [KeyboardButton(text="📕 Bepul darslar haqida"), KeyboardButton(text="📊 Ballarim")],
        [KeyboardButton(text="📱 Telefon raqamim")]
    ], resize_keyboard=True)

    ADMIN_PANEL = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="⬇️ Foydlanuvchilar excel"), KeyboardButton(text="🚀 Xabar yuborish")],
        [KeyboardButton(text="👨🏻‍💻 Adminlar"), KeyboardButton(text="📡 Kanallar")],
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="⚙️ Sozlamalar")],
        [KeyboardButton(text="⬅️ Chiqish")]
    ], resize_keyboard=True)

    SETTINGS = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔐 Yopiq kanal"), KeyboardButton(text="↩️ Ulashish xabari")],
        [KeyboardButton(text="🔗 Taklif havolam xabari"), KeyboardButton(text="📕 Bepul darslar xabari")],
        [KeyboardButton(text="🏃 Start xabari"), KeyboardButton(text="🔢 Odam qo'shish soni")],
        [KeyboardButton(text="⬅️ Orqaga")]
    ], resize_keyboard=True)

    def back(skip: bool = False) -> ReplyKeyboardMarkup:
        if skip:
            return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="➡️ Keyingi")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ], resize_keyboard=True)
        return ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text="⬅️ Orqaga")]
            ], resize_keyboard=True)
        

    @staticmethod
    def confirm_send_ads()-> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="✅ Yuborish")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ], resize_keyboard=True)

class InlineButtons:
    HOME = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Taklif havolam", callback_data="url")]
    ])
    ADMINS_BUTTON = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕", callback_data='add_admin'), InlineKeyboardButton(text="➖", callback_data='remove_admin')]
    ])

    CHANNELS_BUTTON = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕", callback_data='add_channel'), InlineKeyboardButton(text="➖", callback_data='remove_channel')]
    ])

    CHANGE_SHARE_MESSAGE = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ O'zgartirish", callback_data='change_share_message')]
    ])

    CHANGE_ABOUT_LESSONS_MESSAGE = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ O'zgartirish", callback_data='change_about_lessons_message')]
    ])

    CHANGE_START_MESSAGE = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ O'zgartirish", callback_data='change_start_message')]
    ])

    CHANGE_PRIVATE_CHANNEL = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Kanalni o'zgartirish", callback_data='change_private_channel')]
    ])

    @staticmethod
    def chanels(chanels: list[dict]) -> InlineKeyboardMarkup:
        if not chanels:
            chanels = []
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