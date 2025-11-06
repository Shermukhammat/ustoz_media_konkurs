import asyncio
from loader import dp, db, bot
import handlers, middlewares


async def main():
    await db.init()
    db.bot = await bot.get_me()
    print(f"[bot]: @{db.bot.username}")
    await dp.start_polling(bot)
    await db.close()

if __name__ == '__main__':
    asyncio.run(main())