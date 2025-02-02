from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router_client = Router()


from database.db import init_db, register_user, get_categories, get_bouquets_by_category, add_to_cart, get_cart, remove_from_cart
from keyboard import keyboards as kb



@router_client.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    init_db()
    register_user(message.from_user.id, message.from_user.username)
    await message.answer("Добро пожаловать в магазин цветов!", reply_markup=kb.main()) 