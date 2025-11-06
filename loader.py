from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from db import DataBase
import asyncio


db = DataBase("files/config.yaml")
bot = Bot(db.TOKEN)
dp = Dispatcher(storage=MemoryStorage())
