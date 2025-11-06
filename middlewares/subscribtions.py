from aiogram import BaseMiddleware, Router, F, Dispatcher
from aiogram.types import Message, User as TGUser, TelegramObject, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, Any, Awaitable, Callable
from loader import db, dp, bot
from aiogram.dispatcher.event.bases import SkipHandler, CancelHandler
from asyncio import Semaphore
from aiocache import SimpleMemoryCache
# from aiogram.exceptions import ChatAdminRequired, ChatNotFound, Unauthorized

cache = SimpleMemoryCache(ttl = 30)

class SubscribetionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        run = True
        if db.chanels:
            tg_user: TGUser = data["event_from_user"]
            if not await cache.get(tg_user.id):
                run = await check_subscribtion(db.chanels, tg_user, event)
        
        if run:
            return await handler(event, data)



async def is_subscribed(user_id : int, chanel : str):
    try:
        member  = await bot.get_chat_member(chat_id = chanel, user_id = user_id)
        if member and member.status != 'left':
            return True
        return False  
    except Exception as e:
        return False

async def check_subscribtion(check_chanels: list[dict], tg_user: TGUser, event: Message | CallbackQuery):
    chanels = []
    for chanel in check_chanels:
        if not await is_subscribed(tg_user.id, chanel.get('id')):
            chanels.append(chanel)
    
    if chanels:
        replay_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=chanel.get('name', 'Kanal'), url=chanel.get('url'))] for chanel in chanels
        ])
        replay_markup.inline_keyboard.append([InlineKeyboardButton(text="✅ А'zo boʼldim", callback_data="check")])

        
        if isinstance(event, CallbackQuery):
            if event.data == "check":
                await event.answer("❗️ Barcha kanallarga obuna bo'lmadingiz" if db.chanels_len > 1 else "❗️ Kanalga obuna bo'lmadingiz", show_alert=True)
            else:
                await bot.send_message(text = db.need_subscribe_message,
                                       chat_id=tg_user.id,
                                       reply_markup=replay_markup)      
        elif isinstance(event, Message):
            await event.answer(db.need_subscribe_message,
                               reply_markup=replay_markup)
        return False
    
    await cache.set(tg_user.id, True)
    return True


dp.message.middleware(SubscribetionMiddleware())
dp.callback_query.middleware(SubscribetionMiddleware())

print('middlewares set up [true]')