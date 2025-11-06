import asyncpg, asyncio
from asyncpg import Pool, Connection
from .users import UserManger
from .params import ParamsDB
from aiogram.types import User
from .pre_invate import PreInvateManger


class DataBase(ParamsDB, UserManger, PreInvateManger):
    def __init__(self, config : str) -> None:
        ParamsDB.__init__(self, config)
        UserManger.__init__(self)
        PreInvateManger.__init__(self)

        self.pool : Pool = None
        self.bot : User = None

    async def init(self):
        self.pool : Pool = await asyncpg.create_pool(user=self.config.user, 
                                         password=self.config.password,
                                         database=self.config.database, 
                                         host=self.config.host,
                                         port = self.config.port)
        
        if self.pool:
            print("[databse] : connected")
        
        await self.init_users_db()
        await self.init_invate_db()

    async def close(self):
        await self.pool.close()
        print("[databse] : closed")