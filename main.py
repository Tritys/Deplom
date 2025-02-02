import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
import logging


from keyboard import handler_admin
from config import TG_TOKEN
from handler import router


async def main():
    bot = Bot(token=TG_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass