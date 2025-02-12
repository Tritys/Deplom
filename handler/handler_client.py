from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.orm import Session
from database.db import get_categories, get_bouquets_by_category, add_to_cart, get_cart, add_user, get_db
from database.db import User, Category, Bouquet, Cart, Order, Promotion
import logging
from keyboard.keyboard_client import You_tube, get_bouquet_kd, Website
from database.db import AsyncSession

router_client = Router()
logging.basicConfig(level=logging.INFO)
import keyboard.keyboard_client as kb


# Старт
@router_client.message(Command('start'))
async def proess_conact(message: types.Message, state: FSMContext):
    db = AsyncSession()
    user_id = message.from_user.id

    # Проверяем, существует ли пользователь в базе данных
    user = db.query(User).filter(User.user_id == user_id).first()

    if user:
        await message.answer(f"Привет, {user.username}! Вы уже зарегистрированы. \nРады приветствовать в нашем чат бот магазине", reply_markup=kb.main)
    else:
        # Создаем нового пользователя
        new_user = User(
            user_id=user_id,
            first_name=message.from_user.first_name,
            username=message.from_user.username,
            phone=None    # Пока номер телефона не указан
        )
        db.add(new_user)
        db.commit()
        await message.answer("Добро пожаловать! Пожалуйста, зарегистрируйтесь, отправив номер телефона нажав на кнопку с низу.", reply_markup=kb.contact)
    db.close()
    
@router_client.message(F.contact)  # Используем фильтр вместо content_types
async def process_contact(message: types.Message, state: FSMContext):
    logging.info(f"Получен контакт: {message.contact}")
    
    if not message.contact:
        await message.answer("Пожалуйста, отправьте ваш номер телефона.")
        return

    db = AsyncSession()
    user_id = message.from_user.id
    phone_number = message.contact.phone_number

    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        user.phone = phone_number
        db.commit()
        await message.answer("Ваш номер сохранен! ✅", reply_markup=kb.menu)
    else:
        new_user = User(
            user_id=user_id,
            first_name=message.from_user.first_name,
            username=message.from_user.username,
            phone=phone_number
        )
        db.add(new_user)
        db.commit()
        await message.answer("Ваш номер сохранен! ✅", reply_markup=kb.menu)
    db.close()


# Меню
@router_client.message(F.text == "Меню")
async def menu(message: types.Message):
    await message.answer(f"Приветствуем вас в нашем магазине", reply_markup=kb.main)

# Заказать букет
@router_client.message(F.text == "Заказать букет")
async def show_categories(message: Message):
    await message.answer("Выберите категорию:", reply_markup=kb.category1)
    
# назад в заказать букет
@router_client.message(F.text == "назад")
async def show_categories(message: Message):
    await message.answer("Выберите категорию:", reply_markup=kb.category1)
    
# большие букеты
@router_client.message(F.text == "Большие букеты")
async def show_categories(message: Message):
    await message.answer("Выберите большой букет:", reply_markup=kb.category2)
    
    
@router_client.message(F.text == "Большие букеты")
async def show_bouquets_by_category(message: types.Message):
    db = AsyncSession()
    category_name = "Большие букеты"
    category = db.query(Category).filter(Category.name == category_name).first()

    if category:
        bouquets = db.query(Bouquet).filter(Bouquet.category_id == category.id).all()
        if bouquets:
            bouquet = bouquets[0]  # Первый букет в категории
            message_text = f"**{bouquet.name}**\n\n"
            message_text += f"*Описание:* {bouquet.description}\n"
            message_text += f"*Цена:* {bouquet.price} руб.\n"
            if bouquet.discount > 0:
                message_text += f"*Скидка:* {bouquet.discount}%\n"
                message_text += f"*Цена со скидкой:* {bouquet.price * (1 - bouquet.discount / 100):.2f} руб.\n"

            await message.answer_photo(
                photo=bouquet.image_url,
                caption=message_text,
                parse_mode="Markdown",
                reply_markup=get_bouquet_kd(bouquet.id, category.id)
            )
        else:
            await message.answer("В этой категории пока нет букетов. Выберите другую категорию", reply_markup=kb.category2)
    else:
        await message.answer("Категория не найдена. Выберите другую категорию", reply_markup=kb.category2)
    db.close()
# # Меню
# @router_client.message(F.text == "Меню")
# async def show_categories(message: Message):
#     categories = get_categories()
#     await message.answer("Выберите категорию:", reply_markup=kb.category())


# # Категории
# @router_client.message(F.text == "Категории")
# async def show_categories(message: types.Message):
#     categories = get_categories()
#     await message.answer("Выберите категорию:", reply_markup=kb.category())

# Профиль
@router_client.message(F.text == "Профиль")
async def show_profile(message: types.Message):
    db = AsyncSession()
    user_id = message.from_user.id
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        await message.answer(f'''
            Ваш профиль:\n
            Ваш ID: {user.user_id}\n
            Никнейм: {user.username}\n
            Имя: {user.first_name}\n
            Номер телефона: {user.phone}\n
        ''', reply_markup=kb.profile)
    else:
        await message.answer("Профиль не найден. Пожалуйста, пройдите регистрацию используя команду /start")
    db.close()

    
    

# Акции
@router_client.message(F.text == "Акции")
async def show_categories(message: Message):
    db = AsyncSession()
    categories = db.query(Category).all()
    await message.answer("Выберите категорию:", reply_markup=kb.category)
    db.close()

# Адрес магазина
@router_client.message(F.text == "Адрес магазина")
async def show_categories(message: Message):
    await message.answer('''
                         Наш магазин находится по адрессу ...\n
                         Работает каждый день с 9:00 до 18:00 \n
                         Номер телефона для связи с администратором цветочного магазина 87369874326''', reply_markup=kb.shop_address)

# О магазине
@router_client.message(F.text == "О магазине ℹ️")
async def show_categories(message: Message):
    await message.answer('''
                         Всю интересующую вас информацию можно узнать из документа приведённого ниже
                         \nА также на нашем сайте: 

''', reply_markup=kb.shop)
    
    
    
    
    
    
    
    
    

#Корзина
@router_client.message(lambda message: message.text == "Корзина")
async def show_cart(message: types.Message):
    db = AsyncSession()
    cart_items = db.query(Cart).filter(Cart.user_id == message.from_user.id).all()
    if not cart_items:
        await message.answer("Ваша корзина пуста.")
    else:
        cart_text = "Ваша корзина:\n"
        total_price = 0
        for item in cart_items:
            bouquet = db.query(Bouquet).filter(Bouquet.id == item.bouquet_id).first()
            cart_text += f"{bouquet.name} - {bouquet.price} руб. x {item.quantity}\n"
            total_price += bouquet.price * item.quantity
        cart_text += f"Итого: {total_price} руб."
        await message.answer(cart_text, reply_markup=kb.cart())
    db.close()

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
    await message.answer("Выберите категорию:", reply_markup=Website())

# YouTube
@router_client.message(F.text == "YouTube")
async def show_categories(message: Message):
    categories = get_categories()
    await message.answer("Выберите категорию:", reply_markup=You_tube())
