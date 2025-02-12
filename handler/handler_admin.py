from aiogram import Router, F, types
from aiogram.dispatcher import Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import SessionLocal, Category, Bouquet, Promotion
from aiogram.fsm.context import FSMContext

import keyboard.keyboard_client as kb_admin
router_admin = Router()

@router_admin.message(Command('start'))
async def proess_conact(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать! Пожалуйста, зарегистрируйтесь, отправив номер телефона нажав на кнопку с низу.", reply_markup=kb_admin.main_admin)