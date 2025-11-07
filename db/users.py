from asyncpg.pool import PoolAcquireContext, Pool
from asyncpg import Connection
from datetime import datetime
from aiocache import SimpleMemoryCache
from datetime import datetime, timedelta
from pytz import timezone

TZ = timezone('Asia/Tashkent')

class UserStatus:
    active = 1
    blocked = 2

class User:
    def __init__(self,
                 id : int = None,
                 first_name : str = None,
                 last_name : str = None,
                 invited_users : int = 0,
                 registered : datetime = None,
                 is_admin: bool = False,
                 username : str = None,
                 status : int = UserStatus.active,
                 phone_number : str = None
                 ) -> None:
        self.id = id
        self.invited_users = invited_users
        self.first_name = first_name
        self.last_name = last_name
        self.status = status
        self.is_admin = is_admin
        self.username = username
        self.phone_number = phone_number

        if registered:
            self.registered = registered
        else:
            self.registered = datetime.now()

    @property
    def full_name(self) -> str:
        if self.last_name and self.first_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return "Nomalum"
    


    @property
    def registred_readble(self) -> str:
        registered = self.registered.astimezone(TZ)
        return f"{registered.year}.{registered.month}.{registered.day} {registered.hour}:{registered.second}"

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.active


class UserManger:
    def __init__(self) -> None: 
        self.users_cache  = SimpleMemoryCache(ttl = 20)
        self.pool : Pool = None
    
    async def init_users_db(self):
        async with self.pool.acquire() as conn:
            conn: Connection
            await conn.execute("""CREATE TABLE IF NOT EXISTS users
                              (id BIGINT PRIMARY KEY, 
                               first_name TEXT, 
                               last_name TEXT, 
                               registered TIMESTAMP, 
                               status INTEGER,
                               username TEXT,
                               phone_number TEXT,
                               invited_users INTEGER DEFAULT 0,
                               is_admin BOOLEAN DEFAULT FALSE
                           );""")

    async def register_user(self, user : User):
        async with self.pool.acquire() as conn:
            conn: Connection
            await conn.execute(""" INSERT INTO users (id, first_name, last_name, registered, status, username, phone_number) 
                                  VALUES ($1, $2, $3, $4, $5, $6, $7) ON CONFLICT (id) DO NOTHING;""",
                                  user.id, user.first_name, user.last_name, user.registered, user.status, user.username, user.phone_number)
        await self.users_cache.set(user.id, user)
        
    async def get_user(self, id : int) -> User:
        user = await self.users_cache.get(id)
        if user:
            return user
        
        async with self.pool.acquire() as conn:
            conn: Connection
            row = await conn.fetchrow("""SELECT * FROM users WHERE id = $1;""", id)

        if row:
            user = User(id = row['id'], 
                        first_name=row['first_name'], 
                        last_name=row['last_name'],
                        invited_users=row['invited_users'],
                        registered=row['registered'], 
                        status=row['status'], 
                        is_admin=row['is_admin'],
                        username=row['username'],
                        phone_number=row['phone_number'])
            await self.users_cache.set(id, user)
            return user
      
    async def remove_user(self, id : int):
        await self.users_cache.delete(id)
        async with self.pool.acquire() as conn:
            conn: Connection
            await conn.execute("""DELETE FROM users WHERE id = $1;""", id)

    async def update_user(self, id : int, **kwargs):
        async with self.pool.acquire() as conn:
            conn: Connection
            for column, value in kwargs.items():
                await conn.execute(f"""UPDATE users SET {column} = $1 WHERE id = $2;""", value, id)
        await self.users_cache.delete(id)
        
    async def get_useres(self) -> list[User]:
        async with self.pool.acquire() as conn:
            conn : Connection
            rows = await conn.fetch("""SELECT * FROM users;""")
        return [User(id = row['id'], 
                     first_name=row['first_name'], 
                     last_name=row['last_name'],
                     invited_users=row['invited_users'],
                     registered=row['registered'], 
                     status=row['status'], 
                     username=row['username'],
                     phone_number=row['phone_number']) for row in rows]

    async def get_admins(self) -> list[User]:
        async with self.pool.acquire() as conn:
            conn : Connection
            rows = await conn.fetch("""SELECT * FROM users WHERE is_admin = TRUE;""")
        return [User(id = row['id'], 
                     first_name=row['first_name'], 
                     last_name=row['last_name'],
                     invited_users=row['invited_users'],
                     registered=row['registered'], 
                     status=row['status'], 
                     username=row['username'],
                     phone_number=row['phone_number']) for row in rows]