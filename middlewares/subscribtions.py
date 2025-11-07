from aiogram import BaseMiddleware, Router, F, Dispatcher
from aiogram.types import Message, User as TGUser, TelegramObject, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, Any, Awaitable, Callable
from loader import db, dp, bot
from aiogram.dispatcher.event.bases import SkipHandler, CancelHandler
from asyncio import Semaphore
from aiocache import SimpleMemoryCache
from db import PreInvate

cache = SimpleMemoryCache(ttl = 30)
NEED_SUBCRIBE_MESSAGE = "🚀 Loyihada ishtirok etish uchun quyidagi kanalimzga a’zo bo‘ling. Keyin \"✅ A’zo bo‘ldim\" tugmasini bosing"

class SubscribetionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        run = True
        user = await db.get_user(event.from_user.id)
        if not user:
            return await handler(event, data)
        
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
                await event.answer("❗️ Kanalga obuna bo'lmadingiz", show_alert=True)
            else:
                await event.message.answer(NEED_SUBCRIBE_MESSAGE, reply_markup=replay_markup)

        elif isinstance(event, Message):
            await event.answer(NEED_SUBCRIBE_MESSAGE, reply_markup=replay_markup)

        return False
    
    await cache.set(tg_user.id, True)
    return True


async def check_payload(event: Message):
    user = await db.get_user(event.from_user.id)
    if user:
        return
    
    command_text = event.text.strip()
    payload = command_text.split(maxsplit=1)[1] if len(command_text.split()) > 1 else None
    if payload and payload.isnumeric():
        user = await db.get_user(int(payload))
        if not user:
            return
        
        await db.add_pre_invate(PreInvate(invated_user=user.id, user_id=event.from_user.id))


dp.message.middleware(SubscribetionMiddleware())
dp.callback_query.middleware(SubscribetionMiddleware())

print('middlewares set up [true]')