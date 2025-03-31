import asyncio
import os
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
import logging
from datetime import datetime
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import sys
from database.db import create_tables
from dotenv import find_dotenv, load_dotenv, dotenv_values

# Импортируем роутеры
from handler.handler_client import router_client
from handler.handler_admin import router_admin

# Загрузка переменных окружения
load_dotenv(find_dotenv())

# Логирование
start_time = datetime.now()
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
if not load_dotenv(find_dotenv()):
    logger.error("Не найден файл .env")
    sys.exit(1)

TOKEN = os.getenv("TOKEN1")
ADMIN_CHAT_ID = os.getenv("ADMIN_IDS")  # ID администратора

if not TOKEN:
    logger.error("Токен бота не найден в переменных окружения")
    sys.exit(1)
    
if not ADMIN_CHAT_ID:
    logger.error("ID администратора не найден в переменных окружения")
    sys.exit(1)
    
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключение роутеров
dp.include_router(router_client)
dp.include_router(router_admin)

async def notify_admin(message: str):
    """
    Отправляет сообщение администратору.
    """
    try:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения администратору: {e}")

async def main():
    try:
        await create_tables()
        # Уведомление администратора о запуске бота
        await notify_admin(f"🤖 Бот запущен в {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Запуск бота
        logger.info(f"Бот запущен в {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        await notify_admin(f"⚠️ Ошибка при запуске бота: {e}")
        await on_shutdown()
        sys.exit(1)

async def on_shutdown():
    try:
        shutdown_time = datetime.now()
        uptime = shutdown_time - start_time
        logger.info(f"Бот выключен в {shutdown_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Время работы бота: {uptime}")

        # Уведомление администратора о выключении бота
        await notify_admin(f"🛑 Бот выключен в {shutdown_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                          f"⏱ Время работы бота: {uptime}")

        await bot.session.close()
    except Exception as e:
        logger.error(f"Ошибка при выключении бота: {e}")
        await notify_admin(f"⚠️ Ошибка при выключении бота: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения работы")
        asyncio.run(on_shutdown())
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        asyncio.run(notify_admin(f"🚨 Критическая ошибка: {e}"))
        asyncio.run(on_shutdown())