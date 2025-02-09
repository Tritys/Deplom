from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.orm import Session
from database.db import get_db , engine, Base, get_categories, get_bouquets_by_category, add_to_cart, get_cart, add_user
from database.models import User
from keyboard.keyboard_client import You_tube, get_bouquet_kd
from database.db import SessionLocal, User

router_client = Router()

import keyboard.keyboard_client as kb


# Старт
@router_client.message(CommandStart())
async def start_cmd(message: types.Message, callback: types.CallbackQuery):
    db = SessionLocal()
    user_id = message.from_user.id

    # Проверяем, существует ли пользователь в базе данных
    user = db.query(User).filter(User.user_id == user_id).first()

    if user:
        await message.answer(f"Привет, {user.username}! Вы уже зарегистрированы.", reply_markup=kb.menu)
    else:
        # Создаем нового пользователя
        new_user = User(
            user_id=user_id,
            first_name=message.from_user.first_name,
            username=message.from_user.username,
            phone=None  # Пока номер телефона не указан
        )
        db.add(new_user)
        db.commit()
        await callback.message.answer("Добро пожаловать! Пожалуйста, зарегистрируйтесь, отправив номер телефона нажав на кнопку с низу.", reply_markup=kb.contact)
    db.close()

@router_client.message()
async def process_contact(message: types.Message, state: FSMContext):
    if message.contact:  # Проверяем, что это контакт
        user_id = message.from_user.id
        phone_number = message.contact.phone_number

        # Сохранение в БД
        session = SessionLocal()
        user = session.query(User).filter_by(user_id=user_id).first()

        if user:
            user.phone = phone_number  # Обновляем номер
        else:
            new_user = User(user_id=user_id, phone=phone_number)
            session.add(new_user)

        session.commit()
        session.close()

        await message.answer("Ваш номер сохранен! ✅", reply_markup=kb.menu)


# Меню
@router_client.message(F.text == "Меню")
async def show_categories(message: Message):
    categories = get_categories()
    await message.answer("Приветствуем вас в нашем магазине", reply_markup=kb.main)

# Заказать букет
@router_client.message(F.text == "Заказать букет")
async def show_categories(message: Message):
    categories = get_categories()
    await message.answer("Выберите категорию:", reply_markup=kb.category1)
    
# назад в заказать букет
@router_client.message(F.text == "назад")
async def show_categories(message: Message):
    categories = get_categories()
    await message.answer("Выберите категорию:", reply_markup=kb.category1)
    
# большие букеты
@router_client.message(F.text == "Большие букеты")
async def show_categories(message: Message):
    categories = get_categories()
    await message.answer("Выберите большой букет:", reply_markup=kb.category2)
async def show_bouquets_by_category(message: types.Message):
    category_name = message.text
    categories = get_categories()
    category_id = next((cat[0] for cat in categories if cat[1] == category_name), None)

    if category_id:
        bouquets = get_bouquets_by_category(category_id)
        if bouquets:
            bouquet = bouquets[0]  # Первый букет в категории
            bouquet_id, name, price, description, image_url, discount = bouquet

            # Формируем текст сообщения
            message_text = f"**{name}**\n\n"
            message_text += f"*Описание:* {description}\n"
            message_text += f"*Цена:* {price} руб.\n"
            if discount > 0:
                message_text += f"*Скидка:* {discount}%\n"
                message_text += f"*Цена со скидкой:* {price * (1 - discount / 100):.2f} руб.\n"

            # Отправляем фото и описание
            await message.answer_photo(
                photo=image_url,
                caption=message_text,
                parse_mode="Markdown",
                reply_markup=get_bouquet_kd(bouquet_id, category_id)
            )
        else:
            await message.answer("В этой категории пока нет букетов. Выбирете другую категорию", reply_markup=kb.category2)
    else:
        await message.answer("Категория не найдена. Выбирете другую категорию", reply_markup=kb.category2)

# # Меню
# @router_client.message(F.text == "Меню")
# async def show_categories(message: Message):
#     categories = get_categories()
#     await message.answer("Выберите категорию:", reply_markup=kb.category())


# # Категории
# @router_client.message(F.text == "Категории")
# async def show_categories(message: Message):
#     categories = get_categories()
#     await message.answer("Выберите категорию:", reply_markup=kb.category())

# Профиль
@router_client.message(F.text == "Профиль")
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
                         ''', reply_markup=kb.profile)
    else:
        await message.answer("Профиль не найден. Пожалуйста, пройдите регистрацию используя команду /start")

    
    

# Акции
@router_client.message(F.text == "Акции")
async def show_categories(message: Message):
    categories = get_categories()
    await message.answer("Выберите категорию:", reply_markup=kb.category)

# Адрес магазина
@router_client.message(F.text == "Адрес магазина")
async def show_categories(message: Message):
    categories = get_categories()
    await message.answer('''
                         Наш магазин находится по адрессу ...
                         Работает каждый день с 9:00 до 18:00 
                         Номер телефона для связи с администратором цветочного магазина 87369874326''', reply_markup=kb.shop_address)

# О магазине
@router_client.message(F.text == "О магазине ℹ️")
async def show_categories(message: Message):
    categories = get_categories()
    await message.answer('''
                         Всю интересующую вас информацию можно узнать из документа приведённого ниже
                         А также на нашем сайте: 

''', reply_markup=kb.shop)
    
    
    
    
    
    
    
    
    

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



# Сайт
@router_client.message(F.text == "Сайт")
async def show_categories(message: Message):
    categories = get_categories()
    await message.answer("Выберите категорию:", reply_markup=kb.category())

# YouTube
@router_client.message(F.text == "YouTube")
async def show_categories(message: Message):
    categories = get_categories()
    await message.answer("Выберите категорию:", reply_markup=You_tube())
