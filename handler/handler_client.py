from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from database.models import User

router_client = Router()


from database.db import init_db, register_user, get_categories, get_bouquets_by_category, add_to_cart, get_cart, remove_from_cart
from keyboard import keyboards as kb


# Старт
@router_client.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    db: Session = next(get_db())
    telegram_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    register_user(message.from_user.id, message.from_user.username)
    
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
         # Сохранение пользователя в базе
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        await message.reply("Вы успешно зарегистрированы!")
    else:
        await message.answer("Прежде чем воспользоваться нашим ботом нужно пройти регистрация для этого нужно отправить свой номер телефона", reply_markup=kb.contact())
    



# Категории
@router_client.message(lambda message: message.text == "Категории")
async def show_categories(message: Message):
    categories = get_categories()
    await message.answer("Выберите категорию:", reply_markup=kb.category())

# Профиль
@router_client.message(lambda message: message.text == "Профиль")
async def show_categories(message: Message):
    
    """Обработчик команды /profile"""
    db: Session = next(get_db())
    telegram_id = message.from_user.id
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        await message.answer('''
                         Ваш профиль
                         Ваш ID: {message.from_user.id}
                         Никнейм: {message.from_user.username}
                         Имя: {message.from_user.full_name}
                         Номер телефона: {message.from_user.phone_number}
                         ''', reply_markup=kb.profile())
    else:
        await message.answer("Профиль не найден. Пожалуйста, пройдите регистрацию используя команду /start")

    
    
# Сайт
@router_client.message(F.text == "Сайт")
async def show_categories(message: Message):
    categories = get_categories()
    await message.answer("Выберите категорию:", reply_markup=kb.category())

# YouTube
@router_client.message(F.text == "YouTube")
async def show_categories(message: Message):
    categories = get_categories()
    await message.answer("Выберите категорию:", reply_markup=kb.category())

# Акции
@router_client.message(F.text == "Акции")
async def show_categories(message: Message):
    categories = get_categories()
    await message.answer("Выберите категорию:", reply_markup=kb.category())

# Адрес магазина
@router_client.message(F.text == "Адрес магазина")
async def show_categories(message: Message):
    categories = get_categories()
    await message.answer('''
                         Наш магазин находится по адрессу ...
                         Работает каждый день с 9:00 до 18:00 
                         Номер телефона для связи с администратором цветочного магазина 87369874326''', reply_markup=kb.category())

#Корзина
@router_client.message(lambda message: message.text == "Корзина")
async def show_cart(message: Message):
    cart_items = get_cart(message.from_user.id)
    if not cart_items:
        await message.answer("Ваша корзина пуста.")
    else:
        cart_text = "Ваша корзина:\n"
        total_price = 0
        for item in cart_items:
            cart_text += f"{item[1]} - {item[2]} руб.\n"
            total_price += item[2]
        cart_text += f"Итого: {total_price} руб."
        await message.answer(cart_text, reply_markup=kb.cart())

# @router_client.callback_query(lambda c: c.data.startswith('category_'))
# async def show_bouquets(callback_query: types.CallbackQuery):
#     category_id = int(callback_query.data.split('_')[1])
#     bouquets = get_bouquets_by_category(category_id)
#     user_data[callback_query.from_user.id] = {"bouquets": bouquets, "current_index": 0}
#     await show_bouquet(callback_query)

# async def show_bouquet(callback_query: types.CallbackQuery):
#     user_id = callback_query.from_user.id
#     bouquets = user_data[user_id]["bouquets"]
#     current_index = user_data[user_id]["current_index"]
#     await callback_query.message.edit_text(
#         f"Букет: {bouquets[current_index][2]}",
#         reply_markup=get_bouquets_keyboard(bouquets, current_index)
#     )

# @router_client.callback_query(lambda c: c.data.startswith('prev_'))
# async def prev_bouquet(callback_query: types.CallbackQuery):
#     user_id = callback_query.from_user.id
#     current_index = int(callback_query.data.split('_')[1])
#     user_data[user_id]["current_index"] = (current_index - 1) % len(user_data[user_id]["bouquets"])
#     await show_bouquet(callback_query)

# @router_client.callback_query(lambda c: c.data.startswith('next_'))
# async def next_bouquet(callback_query: types.CallbackQuery):
#     user_id = callback_query.from_user.id
#     current_index = int(callback_query.data.split('_')[1])
#     user_data[user_id]["current_index"] = (current_index + 1) % len(user_data[user_id]["bouquets"])
#     await show_bouquet(callback_query)

# @router_client.callback_query(lambda c: c.data.startswith('add_'))
# async def add_to_cart_handler(callback_query: types.CallbackQuery):
#     bouquet_id = int(callback_query.data.split('_')[1])
#     add_to_cart(callback_query.from_user.id, bouquet_id)
#     await callback_query.answer("Букет добавлен в корзину!")

# @router_client.callback_query(lambda c: c.data.startswith('remove_'))
# async def remove_from_cart_handler(callback_query: types.CallbackQuery):
#     bouquet_id = int(callback_query.data.split('_')[1])
#     remove_from_cart(callback_query.from_user.id, bouquet_id)
#     await callback_query.answer("Букет удален из корзины!")
#     await show_cart(callback_query.message)

# @router_client.callback_query(lambda c: c.data == 'checkout')
# async def checkout(callback_query: types.CallbackQuery):
#     cart_items = get_cart(callback_query.from_user.id)
#     if not cart_items:
#         await callback_query.answer("Ваша корзина пуста.")
#     else:
#         total_price = sum(item[2] for item in cart_items)
#         await callback_query.answer(f"Заказ оформлен! Сумма к оплате: {total_price} руб.")
#         remove_from_cart(callback_query.from_user.id, None)