import asyncio
import os
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
import logging
from datetime import datetime
from aiogram.enums import ParseMode

from database.db import create_tables
from dotenv import find_dotenv, load_dotenv

# from keyboard import handler_admin
from handler.handler_client import router_client
# from handler.handler_admin import admin_router
from handler import router

start_time = datetime.now()
logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTM)
dp = Dispatcher()

# dp.include_router(admin_router)
dp.include_router(router_client)

load_dotenv(find_dotenv())
async def main():
    bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTM)
    dp = Dispatcher()
    dp.include_router(router)
    
    await dp.start_polling(bot)

async def on_shutdown(dp):
    shutdown_time = datetime.now()
    uptime = shutdown_time - start_time
    logging.info(f"Бот выключен в {shutdown_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Время работы бота: {uptime}")
    
if __name__ == '__main__':
    try:
        create_tables()
        asyncio.run(main())
        print("Бот запущен!")
        logging.info(f"Бот запущен в {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    except KeyboardInterrupt:
        pass
    