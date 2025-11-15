from db import DataBase
import asyncio 

db = DataBase("files/config.yaml")
async def main():
    await db.init() 
    await db.clean_activity()  
    await db.close()


if __name__ == '__main__':
    asyncio.run(main())