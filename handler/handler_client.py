from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from database.db import get_categories, get_bouquets_by_category, add_to_cart, get_cart, add_user, get_db
from database.db import User, Category, Bouquet, Cart, Order, Promotion
import logging
from keyboard.keyboard_client import You_tube, get_bouquet_kd, Website, delivery_keyboard, payment_keyboard 
from database.db import AsyncSession

router_client = Router()
logging.basicConfig(level=logging.INFO)
import keyboard.keyboard_client as kb

# Состояния для FSM
class OrderState(StatesGroup):
    choosing_delivery = State()
    choosing_payment = State()


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
    
value2 = ['День Рождение', '8 марта', 'в корзине', 'в коробке', 
          'Мужские', 'Свадебные', 'Спасибо', 'Извини', 'День матери', 'Монобукет', 'Траурные', 'Искусственные', 'Цветы по штучно']

value1 = ['Розы', 'Тюльпаны', 'Хризантемы', 'Ромашки', 'Лилии', 'Гортензии', 'Ирисы', 'Нарцисы', 'Пионы', 'Эустома', 'Траурные', 'Составные']

@router_client.message(F.text.in_(value2))
# Общая функция для обработки категорий
async def handle_category(message: types.Message, category_name: str):
    db = AsyncSession()
    try:
        result = await db.execute(select(Category).filter(Category.name == category_name))
        category = result.scalars().first()

        if category:
            result = await db.execute(select(Bouquet).filter(Bouquet.category_id == category.id))
            bouquets = result.scalars().all()

            if bouquets:
                bouquet = bouquets[0]  # Показываем первый букет в категории
                await message.answer_photo(
                    photo=bouquet.image_url,  # Если есть URL изображения
                    caption=f"Букет: {bouquet.name}\nОписание: {bouquet.description}\nЦена: {bouquet.price} руб.",
                    reply_markup=get_bouquet_kd(bouquet.id, category.id)
                )
            else:
                await message.answer("В этой категории пока нет букетов.")
        else:
            await message.answer("Категория не найдена.")
    finally:
        await db.close()

# Общая функция для обработки категорий
async def handle_category(message: types.Message, category_name: str):
    db = AsyncSession()
    try:
        result = await db.execute(select(Category).filter(Category.name == category_name))
        category = result.scalars().first()

        if category:
            result = await db.execute(select(Bouquet).filter(Bouquet.category_id == category.id))
            bouquets = result.scalars().all()

            if bouquets:
                bouquet = bouquets[0]  # Показываем первый букет в категории
                await message.answer_photo(
                    photo=bouquet.image_url,  # Если есть URL изображения
                    caption=f"Букет: {bouquet.name}\nОписание: {bouquet.description}\nЦена: {bouquet.price} руб.",
                    reply_markup=get_bouquet_kd(bouquet.id, category.id)
                )
            else:
                await message.answer("В этой категории пока нет букетов.")
        else:
            await message.answer("Категория не найдена.")
    finally:
        await db.close()

# Обработка категорий из value2
@router_client.message(F.text.in_(value2))
async def handle_category_selection(message: types.Message):
    category_name = message.text  # Получаем название категории из текста сообщения
    await handle_category(message, category_name)  # Передаем category_name

# Обработка категорий из value1
@router_client.message(F.text.in_(value1))
async def show_bouquets_by_category2(message: types.Message):
    category_name = message.text  # Получаем название категории из текста сообщения
    await handle_category(message, category_name)  # Передаем category_name

# Листание букетов
@router_client.callback_query(F.data.startswith("prev_") | F.data.startswith("next_"))
async def navigate_bouquets(callback: CallbackQuery):
    db = AsyncSession()
    try:
        data = callback.data.split("_")
        action = data[0]
        bouquet_id = int(data[1])
        category_id = int(data[2])

        result = await db.execute(select(Bouquet).filter(Bouquet.category_id == category_id))
        bouquets = result.scalars().all()
        current_index = next((i for i, b in enumerate(bouquets) if b.id == bouquet_id), 0)

        if action == "prev":
            new_index = (current_index - 1) % len(bouquets)
        else:
            new_index = (current_index + 1) % len(bouquets)

        bouquet = bouquets[new_index]
        await callback.message.edit_text(
            f"Букет: {bouquet.name}\nОписание: {bouquet.description}\nЦена: {bouquet.price} руб.",
            reply_markup=get_bouquet_kd(bouquet.id, category_id)
        )
    finally:
        await db.close()
    
# Добавление в корзину
@router_client.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: CallbackQuery):
    db = AsyncSession()
    try:
        bouquet_id = int(callback.data.split("_")[1])
        user_id = callback.from_user.id

        cart_item = Cart(user_id=user_id, bouquet_id=bouquet_id)
        db.add(cart_item)
        await db.commit()
        await callback.answer("Букет добавлен в корзину!")
    finally:
        await db.close()

# назад в заказать букет
@router_client.message(F.text == "назад")
async def show_categories(message: Message):
    await message.answer("Выберите категорию:", reply_markup=kb.category1)
    
# большие букеты
@router_client.message(F.text == "Большие букеты")
async def show_categories(message: Message):
    await message.answer("Выберите большой букет:", reply_markup=kb.category2)

    
@router_client.message(F.text.in_(value1))
async def show_bouquets_by_category2(message: types.Message):
    db = AsyncSession()
    category_name = message.text
    category = db.query(Category).filter(Category.name == category_name).first()

    if category:
        bouquets = db.query(Bouquet).filter(Bouquet.category_id == category.id).all()
        if bouquets:
            bouquet = bouquets[0]  # Показываем первый букет в категории
            await message.answer_photo(
                photo=bouquet.image_url,  # Если есть URL изображения
                caption=f"Букет: {bouquet.name}\nОписание: {bouquet.description}\nЦена: {bouquet.price} руб.",
                reply_markup=get_bouquet_kd(bouquet.id, category.id)
            )
        else:
            await message.answer("В этой категории пока нет букетов.")
    else:
        await message.answer("Категория не найдена.")
    db.close()

# Профиль
@router_client.message(F.text == "Профиль")
async def show_profile(message: types.Message):
    db = AsyncSession()
    user_id = message.from_user.id
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        await message.answer(f'Ваш профиль:\nВаш ID: {user.user_id}\nНикнейм: {user.username}\nИмя: {user.first_name}\nНомер телефона: {user.phone}\n', reply_markup=kb.profile)
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
    await message.answer('Наш магазин находится по адрессу ...\nРаботает каждый день с 9:00 до 18:00 \nНомер телефона для связи с администратором цветочного магазина 87369874326', reply_markup=kb.shop_address)

# О магазине
@router_client.message(F.text == "О магазине ℹ️")
async def show_categories(message: Message):
    await message.answer('Всю интересующую вас информацию можно узнать из документа приведённого ниже\nА также на нашем сайте: ', reply_markup=kb.shop)

#Корзина
@router_client.message(lambda message: message.text == "Корзина")
async def show_cart(message: types.Message, state: FSMContext):
    db = AsyncSession()
    cart_items = db.query(Cart).filter(Cart.user_id == message.from_user.id).all()
    if not cart_items:
        await message.answer("Ваша корзина пуста.")
    else:
        total_price = 0
        cart_text = "Ваша корзина:\n"
        for item in cart_items:
            bouquet = db.query(Bouquet).filter(Bouquet.id == item.bouquet_id).first()
            cart_text += f"{bouquet.name} - {bouquet.price} руб. x {item.quantity}\n"
            total_price += bouquet.price * item.quantity
        cart_text += f"Итого: {total_price} руб."
        await message.answer(cart_text, reply_markup=delivery_keyboard)
        await state.set_state(OrderState.choosing_delivery)
    db.close()


# Выбор доставки
@router_client.message(OrderState.choosing_delivery)
async def choose_delivery(message: Message, state: FSMContext):
    await state.update_data(delivery_type=message.text)
    await message.answer("Выберите способ оплаты:", reply_markup=payment_keyboard)
    await state.set_state(OrderState.choosing_payment)

# Выбор оплаты
@router_client.message(OrderState.choosing_payment)
async def choose_payment(message: Message, state: FSMContext):
    data = await state.get_data()
    delivery_type = data["delivery_type"]
    payment_method = message.text

    db = AsyncSession()
    cart_items = db.query(Cart).filter(Cart.user_id == message.from_user.id).all()
    total_price = sum(item.bouquet.price * item.quantity for item in cart_items)

    order = Order(
        user_id=message.from_user.id,
        delivery_type=delivery_type,
        payment_method=payment_method,
        total_price=total_price
    )
    db.add(order)
    db.commit()

    await message.answer(f"Заказ оформлен!\nДоставка: {delivery_type}\nОплата: {payment_method}\nИтого: {total_price} руб.", reply_markup=kb.cart)
    await state.clear()
    db.close()



# Сайт
@router_client.message(F.text == "Сайт")
async def show_categories(message: Message):
    await message.answer("Нажмите на ссылку ниже чтобы перейти на наш сайт", reply_markup=Website())

# YouTube
@router_client.message(F.text == "YouTube")
async def show_categories(message: Message):
    await message.answer("Нажмите на ссылку ниже чтобы перейти на наш YouTube канал", reply_markup=You_tube())
