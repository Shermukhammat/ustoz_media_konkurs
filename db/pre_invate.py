from asyncpg.pool import PoolAcquireContext, Pool
from asyncpg import Connection
from datetime import datetime
from aiocache import SimpleMemoryCache
from datetime import datetime, timedelta
from pytz import timezone
from typing import Union


class PreInvate:
    def __init__(self, invated_user: int, user_id: int):
        self.invated_user = invated_user 
        self.user_id = user_id

class PreInvateManger:
    def __init__(self) -> None: 
        self.pool : Pool = None
    
    async def init_invate_db(self):
        async with self.pool.acquire() as conn:
            conn: Connection
            await conn.execute(""" CREATE TABLE IF NOT EXISTS pre_invate (
                               invated_user BIGINT,
                               user_id BIGINT UNIQUE,
                               UNIQUE (invated_user, user_id)
                               ); """)
    
    async def add_pre_invate(self, p: PreInvate) -> bool:
        async with self.pool.acquire() as conn:
            conn: Connection
            result = await conn.execute("""
            INSERT INTO pre_invate (invated_user, user_id)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO NOTHING;
        """, p.invated_user, p.user_id)

        # asyncpg returns strings like "INSERT 0 1" or "INSERT 0 0"
        return result == "INSERT 0 1"  
    
    async def get_pre_invate(self, user_id : int) -> Union[PreInvate, None]:
        async with self.pool.acquire() as conn:
            conn: Connection
            row = await conn.fetchrow("""SELECT * FROM pre_invate WHERE user_id = $1;""", user_id)
        
        if row:
            return PreInvate(invated_user=row['invated_user'], user_id=row['user_id'])