import asyncio
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
import logging
from database.db import create_tables

from dotenv import find_dotenv, load_dotenv

from keyboard import handler_admin
from handler import admin_router, router_client
from config import TG_TOKEN
from handler import router

storage = MemoryStorage()


load_dotenv(find_dotenv())
async def main():
    bot = Bot(token=TG_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        create_tables()
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    