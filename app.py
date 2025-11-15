import asyncio
from loader import dp, db, bot
import handlers, middlewares
from utils.mytime import get_next_day_sec

async def main():
    await db.init()
    db.bot = await bot.get_me()
    print(f"[bot]: @{db.bot.username}")
    asyncio.create_task(dayly_loop())
    await dp.start_polling(bot)
    await db.close()


async def dayly_loop():
    while True:
        await asyncio.sleep(get_next_day_sec())
        await db.clean_activity()


if __name__ == '__main__':
    asyncio.run(main())