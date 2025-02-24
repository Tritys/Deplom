from aiogram import Router, F, types
import io
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.future import select
from aiogram.types import InputMediaPhoto, InputFile
from database.db import get_categories, get_bouquets_by_category, add_to_cart, get_cart, add_user, get_db, get_user
from database.db import User, Category, Bouquet, Cart, Order, Promotion
import logging
from keyboard.keyboard_client import You_tube, get_bouquet_kd, Website, delivery_keyboard, payment_keyboard 
from database.db import AsyncSessionLocal

router_client = Router()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import keyboard.keyboard_client as kb

# Состояния для FSM
class OrderState(StatesGroup):
    choosing_delivery = State()
    choosing_payment = State()


# Старт
@router_client.message(Command('start'))
async def proess_conact(message: types.Message, state: FSMContext):
    async with AsyncSessionLocal() as db:
        user_id = message.from_user.id
        user = await get_user(db, user_id)
        if user:
            await message.answer(f"Привет, {user.username}! Вы уже зарегистрированы.", reply_markup=kb.main)
        else:
            new_user = User(
                user_id=user_id,
                first_name=message.from_user.first_name,
                username=message.from_user.username,
                phone=None
            )
            db.add(new_user)
            await db.commit()
            await message.answer("Добро пожаловать! Пожалуйста, зарегистрируйтесь.", reply_markup=kb.contact)

@router_client.message(F.contact)  # Используем фильтр вместо content_types
async def process_contact(message: types.Message, state: FSMContext):
    logger.info(f"Получен контакт: {message.contact}")
    
    if not message.contact:
        await message.answer("Пожалуйста, отправьте ваш номер телефона.")
        return

    async with AsyncSessionLocal() as db:
        user_id = message.from_user.id
        phone_number = message.contact.phone_number

        try:
            query = select(User).where(User.user_id == user_id)
            result = await db.execute(query)
            user = result.scalars().first()

            if user:
                user.phone = phone_number
                await db.commit()
                await message.answer("Ваш номер сохранен! ✅", reply_markup=kb.menu)
            else:
                new_user = User(
                    user_id=user_id,
                    first_name=message.from_user.first_name,
                    username=message.from_user.username,
                    phone=phone_number
                )
                db.add(new_user)
                await db.commit()
                await message.answer("Ваш номер сохранен! ✅", reply_markup=kb.menu)
        except Exception as e:
            logger.error(f"Ошибка при обработке контакта: {e}")
            await db.rollback()
            await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")
            
# Меню
@router_client.message(F.text == "Меню")
async def menu(message: types.Message):
    await message.answer(f"Приветствуем вас в нашем магазине", reply_markup=kb.main)

# Заказать букет
@router_client.message(F.text == "Заказать букет")
async def show_categories(message: Message):
    await message.answer("Выберите категорию:", reply_markup=kb.category1)
    
async def save_edited_promotion(event, data):
    try:
        promotion_id = data.get('promotion_id')
        if promotion_id is None:
            # Логируем ошибку или возвращаем сообщение об ошибке
            logger.error("promotion_id отсутствует в данных")
            await event.answer("Ошибка: promotion_id не найден.")
            return

        # Ваша логика обработки promotion_id
        # Например:
        # promotion = await get_promotion_by_id(promotion_id)
        # if promotion:
        #     await update_promotion(promotion, data)
        # else:
        #     await event.answer("Акция не найдена.")

    except Exception as e:
        logger.error(f"Ошибка в save_edited_promotion: {e}")
        await event.answer(f"Произошла ошибка: {e}")
    
@router_client.callback_query(F.data.startswith("edit_promotion_"))
async def handle_edit_promotion(callback: CallbackQuery, state: FSMContext):
    try:
        # Предполагаем, что данные callback имеют вид "edit_promotion_<promotion_id>"
        promotion_id = int(callback.data.split("_")[-1])
        if not promotion_id:
            await callback.answer("Ошибка: promotion_id отсутствует.")
            return

        # Сохраняем promotion_id в состоянии
        await state.update_data(promotion_id=promotion_id)

        # Вызываем функцию для сохранения изменений
        await save_edited_promotion(callback, await state.get_data())

    except Exception as e:
        await callback.answer(f"Произошла ошибка: {e}")
    
value2 = ['День Рождение', '8 марта', 'в корзине', 'в коробке', 
          'Мужские', 'Свадебные', 'Спасибо', 'Вместо извенений', 'День матери', 'Монобукеты', 'Траурные', 'Искусственные', 'Цветы по штучно']

value1 = ['Розы', 'Тюльпаны', 'Хризантемы', 'Ромашки', 'Лилии', 'Гортензии', 'Ирисы', 'Нарциссы', 'Пионы', 'Эустома', 'Траурные', 'Составные']

@router_client.message(F.text.in_(value2 + value1) or F.data.startswith("category"))
# Общая функция для обработки категорий
async def handle_category1(message: types.Message, state: FSMContext):
     async with AsyncSessionLocal() as db:
        try:
            category_name = message.text
            result = await db.execute(select(Category).filter(Category.name == category_name))
            category = result.scalars().first()

            if category:
                result = await db.execute(select(Bouquet).filter(Bouquet.category_id == category.category_id))
                bouquets = result.scalars().all()

                if bouquets:
                    bouquet = bouquets[0]  # Показываем первый букет в категории
                    # Проверяем, есть ли изображение
                    if bouquet.image_url:
                        await message.answer_photo(
                            photo=bouquet.image_url,
                            caption=f"Букет: {bouquet.name}\nОписание: {bouquet.description}\nЦена: {bouquet.price} руб.",
                            reply_markup=get_bouquet_kd(bouquet.bouquet_id, category.category_id)
                        )
                    else:
                        # Если изображение отсутствует, отправляем текстовое сообщение
                        await message.answer(
                            f"Букет: {bouquet.name}\nОписание: {bouquet.description}\nЦена: {bouquet.price} руб.\n\nИзображение отсутствует.",
                            reply_markup=get_bouquet_kd(bouquet.bouquet_id, category.category_id)
                        )
                else:
                    await message.answer("В этой категории пока нет букетов.")
            else:
                await message.answer("Категория не найдена.")
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")

# Обработка категорий из value2
@router_client.message(F.text.in_(value2 + value1))
async def handle_category_selection(message: types.Message):
    await handle_category1(message)  # Передаем category_name

# Общая функция для обработки категорий
async def handle_category(message: types.Message):
    async with AsyncSessionLocal() as db:  # Используем контекстный менеджер
        try:
            category_name = message.text  # Получаем название категории из текста сообщения
            result = await db.execute(select(Category).filter(Category.name == category_name))
            category = result.scalars().first()

            if category:
                result = await db.execute(select(Bouquet).filter(Bouquet.category_id == category.category_id))
                bouquets = result.scalars().all()

                if bouquets:
                    bouquet = bouquets[0]  # Показываем первый букет в категории
                    await message.answer_photo(
                        photo=bouquet.image_url,  # Если есть URL изображения
                        caption=f"Букет: {bouquet.name}\nОписание: {bouquet.description}\nЦена: {bouquet.price} руб.",
                        reply_markup=get_bouquet_kd(bouquet.bouquet_id, category.category_id)
                    )
                else:
                    await message.answer("В этой категории пока нет букетов.")
            else:
                await message.answer("Категория не найдена.")
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")



# Листание букетов
@router_client.callback_query(F.data.startswith("prev_") | F.data.startswith("next_"))
async def navigate_bouquets(callback: CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as db:  # Используем асинхронный контекстный менеджер
        try:
            # Разбираем callback data
            data = callback.data.split("_")
            action = data[0]  # "prev" или "next"
            bouquet_id = int(data[1])  # ID текущего букета
            category_id = int(data[2])  # ID категории

            # Получаем все букеты в категории
            result = await db.execute(select(Bouquet).filter(Bouquet.category_id == category_id))
            bouquets = result.scalars().all()
            
            # Если букетов нет, выводим сообщение
            if not bouquets:
                await callback.answer("В этой категории пока нет букетов.")
                return

            # Находим индекс текущего букета
            current_index = next((i for i, b in enumerate(bouquets) if b.bouquet_id == bouquet_id), 0)
            
            

            # Определяем новый индекс в зависимости от действия
            if action == "prev":
                new_index = (current_index - 1) % len(bouquets)
            else:
                new_index = (current_index + 1) % len(bouquets)

            # Получаем новый букет
            new_bouquet = bouquets[new_index]
            
            # Проверяем, есть ли изображение
            if new_bouquet.image_url:
                # Если image_url - это URL, используем его
                if isinstance(new_bouquet.image_url, str):
                    media = InputMediaPhoto(
                        media=new_bouquet.image_url,
                        caption=f"Букет: {new_bouquet.name}\nОписание: {new_bouquet.description}\nЦена: {new_bouquet.price} руб."
                    )
                # Если image_url - это бинарные данные, преобразуем их в InputFile
                else:
                    image_file = InputFile(io.BytesIO(new_bouquet.image_url), filename="bouquet.jpg")
                    media = InputMediaPhoto(
                        media=image_file,
                        caption=f"Букет: {new_bouquet.name}\nОписание: {new_bouquet.description}\nЦена: {new_bouquet.price} руб."
                    )
            else:
                await callback.answer("Изображение отсутствует.")
                return

            # Обновляем медиа и клавиатуру
            await callback.message.edit_media(
                media=media,
                reply_markup=get_bouquet_kd(new_bouquet.bouquet_id, category_id)
            )
        except Exception as e:
            await callback.answer(f"Произошла ошибка: {e}")
    
# Добавление в корзину
@router_client.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as db:
        try:
            data = await state.get_data()
            bouquet_id = data.get("bouquet_id")
            
            if not bouquet_id:
                await callback.answer("Букет не выбран. Пожалуйста, выберите букет сначала.")
                return

            user_id = callback.from_user.id

            cart_item = Cart(user_id=user_id, bouquet_id=bouquet_id)
            db.add(cart_item)
            await db.commit()
            await callback.answer("Букет добавлен в корзину!")
        except Exception as e:
            await callback.answer(f"Произошла ошибка: {e}")

# назад в заказать букет
@router_client.message(F.text == "назад")
async def show_categories6(message: Message):
    await message.answer("Выберите категорию:", reply_markup=kb.category1)
    
# большие букеты
@router_client.message(F.text == "Большие букеты")
async def show_categories7(message: Message):
    await message.answer("Выберите большой букет:", reply_markup=kb.category2)

# Профиль
@router_client.message(F.text == "Профиль")
async def show_profile(message: types.Message):
    # Открываем асинхронную сессию с базой данных
    async with AsyncSessionLocal() as db:
        user_id = message.from_user.id

        # Создаем асинхронный запрос к базе данных
        query = select(User).where(User.user_id == user_id)
        result = await db.execute(query)
        user = result.scalars().first()

        # Проверяем, найден ли пользователь
        if user:
            await message.answer(
                f"Ваш профиль:\n"
                f"Ваш ID: {user.user_id}\n"
                f"Никнейм: {user.username}\n"
                f"Имя: {user.first_name}\n"
                f"Номер телефона: {user.phone}\n",
                reply_markup=kb.profile,
            )
        else:
            await message.answer(
                "Профиль не найден. Пожалуйста, пройдите регистрацию, используя команду /start"
            )
# Акции
@router_client.message(F.text == "Акции")
async def show_categories1(message: Message):
    db = AsyncSessionLocal ()
    categories = db.execute(Category).all()
    await message.answer("Выберите категорию:", reply_markup=kb.category)
    db.close()

# Адрес магазина
@router_client.message(F.text == "Адрес магазина")
async def show_categories2(message: Message):
    await message.answer('Наш магазин находится по адрессу ...\nРаботает каждый день с 9:00 до 18:00 \nНомер телефона для связи с администратором цветочного магазина 87369874326', reply_markup=kb.shop_address)

# О магазине
@router_client.message(F.text == "О магазине ℹ️")
async def show_categories3(message: Message):
    await message.answer('Всю интересующую вас информацию можно узнать из документа приведённого ниже\nА также на нашем сайте: ', reply_markup=kb.shop)

#Корзина
@router_client.message(lambda message: message.text == "Корзина")
async def show_cart(message: types.Message, state: FSMContext):
    # Открываем асинхронную сессию с базой данных
    async with AsyncSessionLocal() as db:
        user_id = message.from_user.id

        # Запрос для получения товаров в корзине пользователя
        cart_query = select(Cart).where(Cart.user_id == user_id)
        cart_result = await db.execute(cart_query)
        cart_items = cart_result.scalars().all()

        # Если корзина пуста
        if not cart_items:
            await message.answer("Ваша корзина пуста.")
        else:
            total_price = 0
            cart_text = "Ваша корзина:\n"

            # Перебираем товары в корзине
            for item in cart_items:
                # Запрос для получения информации о букете
                bouquet_query = select(Bouquet).where(Bouquet.id == item.bouquet_id)
                bouquet_result = await db.execute(bouquet_query)
                bouquet = bouquet_result.scalars().first()

                # Добавляем информацию о букете в текст корзины
                if bouquet:
                    cart_text += f"{bouquet.name} - {bouquet.price} руб. x {item.quantity}\n"
                    total_price += bouquet.price * item.quantity

            # Добавляем итоговую стоимость
            cart_text += f"Итого: {total_price} руб."

            # Отправляем сообщение с содержимым корзины
            await message.answer(cart_text, reply_markup=delivery_keyboard)

            # Устанавливаем состояние выбора доставки
            await state.set_state(OrderState.choosing_delivery)



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

    db = AsyncSessionLocal ()
    cart_items = db.execute(Cart).filter(Cart.user_id == message.from_user.id).all()
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

@router_client.message(F.text == "Связь с администратором")
async def communication_with_administrator(message: Message):
    await message.answer("Выбирете способ связи с администратором", reply_markup=kb.admin_contact)

@router_client.message(F.text == "Позвонить")
async def call(message: Message):
    await message.answer("Вы можете связаться с администратором позвонив на номер +723569227455", reply_markup=kb.contact_as)
    
@router_client.message(F.text == "В чате")
async def In_chat(message: Message):
    await message.answer("Напишите вашу притензию @Sertaw", reply_markup=kb.contact_as)

# Сайт
@router_client.message(F.text == "Сайт")
async def Web_site(message: Message):
    await message.answer("Нажмите на ссылку ниже чтобы перейти на наш сайт", reply_markup=Website())

# YouTube
@router_client.message(F.text == "YouTube")
async def You_Tube(message: Message):
    await message.answer("Нажмите на ссылку ниже чтобы перейти на наш YouTube канал", reply_markup=You_tube())
    
    
@router_client.message()
async def unknown_message(message: types.Message):
    await message.answer("Я тебя не понимаю. Попробуй выбрать команду из меню.")