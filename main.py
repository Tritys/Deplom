import asyncio
import os
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
import logging
from datetime import datetime
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from database.db import create_tables
from dotenv import find_dotenv, load_dotenv, dotenv_values

# Импортируем роутеры
from handler.handler_client import router_client
# from handler.handler_admin import admin_router

# Загрузка переменных окружения

load_dotenv(find_dotenv())

# Логирование
start_time = datetime.now()
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TOKEN1")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключение роутеров
dp.include_router(router_client)
# dp.include_router(admin_router)

async def main():
    # Создание таблиц в базе данных
    create_tables()

    # Запуск бота
    logging.info(f"Бот запущен в {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    await dp.start_polling(bot)

async def on_shutdown():
    shutdown_time = datetime.now()
    uptime = shutdown_time - start_time
    logging.info(f"Бот выключен в {shutdown_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Время работы бота: {uptime}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(on_shutdown())