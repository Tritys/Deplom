from aiogram import Router, F, types
import io
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, CallbackQuery
from sqlalchemy import update, delete, select, func
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold, hunderline
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.future import select
from aiogram.types import InputMediaPhoto, InputFile
from database.db import  get_user
from database.db import User, Category, Bouquet, Cart, Order, OrderItem
import logging
from keyboard.keyboard_client import You_tube, get_bouquet_kd, Website, get_cart_keyboard, get_payment_keyboard, get_delivery_keyboard, help_keyboard, promotions, contacts
from database.db import AsyncSessionLocal
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram import Bot
import os
import logging
from datetime import datetime

router_client = Router()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import keyboard.keyboard_client as kb

ADMIN_CHAT_ID = int(os.getenv("ADMIN_IDS"))

async def notify_admin(bot: Bot, message: str):
    """
    Отправляет сообщение администратору.
    """
    try:
        await bot.send_message(ADMIN_CHAT_ID, message)
    except TelegramBadRequest as e:
        logger.error(f"Ошибка при отправке сообщения администратору: {e}")
        if "chat not found" in str(e):
            logger.error(f"Чат с администратором не найден. Убедитесь, что chat_id корректен.")
    except TelegramAPIError as e:
        logger.error(f"Ошибка при отправке сообщения администратору: {e}")



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
        await message.answer("Пожалуйста, отправьте ваш номер телефона по кнопке.")
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
@router_client.message(F.text == "Меню" or F.text == "🔙 Меню")
async def menu(message: types.Message):
    await message.answer(f"Приветствуем вас в нашем магазине", reply_markup=kb.main)
    
# Меню
@router_client.message(F.data.startswith("menu_"))
async def menu(message: types.Message):
    await message.answer(f"Приветствуем вас в нашем магазине", reply_markup=kb.main)

# Заказать букет
@router_client.message(F.text == "Заказать букет" or F.data.startswith("categorys"))
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
          'Мужские', 'Свадебные', 'Спасибо', 'Вместо извинений', 'День матери', 'Монобукеты', 'Траурные', 'Искусственные']

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
            bouquet_id = int(callback.data.split("_")[1])  # Извлекаем bouquet_id
            user_id = callback.from_user.id

            # Проверяем, есть ли уже такой букет в корзине
            cart_item_query = select(Cart).where(
                Cart.user_id == user_id,
                Cart.bouquet_id == bouquet_id
            )
            cart_item_result = await db.execute(cart_item_query)
            cart_item = cart_item_result.scalars().first()

            if cart_item:
                # Если букет уже в корзине, увеличиваем количество
                cart_item.quantity += 1
            else:
                # Если букета нет в корзине, добавляем его
                cart_item = Cart(user_id=user_id, bouquet_id=bouquet_id, quantity=1)
                db.add(cart_item)

            await db.commit()
            

            # Удаляем старое сообщение с корзиной
            # await callback.message.delete()

            # Отправляем новое сообщение с обновленной корзиной
            # await show_cart(callback.message, state=state)

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

# # Акции
# @router_client.message(F.text == "🎁 Акции")
# async def show_promotions(message: Message):
#     async with AsyncSessionLocal() as db:
#         active_promos = await db.execute(
#             select(Promotion)
#             .where(Promotion.end_date >= func.now())
#         )
#         promos = active_promos.scalars().all()
        
#         if not promos:
#             await message.answer(
#                 "В данный момент активных акций нет.\n"
#                 "Следите за обновлениями!",
#                 reply_markup=promotions
#             )
#             return
        
#         promos_text = "🎁 *Действующие акции*\n\n"
#         for promo in promos:
#             promos_text += f"""
# 🎉 {promo.title}
# 📝 {promo.description}
# 💰 Скидка: {promo.discount}%
# 📅 До: {promo.end_date}
#             """
        
#         await message.answer(promos_text, reply_markup=promotions)


# Адрес магазина
@router_client.message(F.text == "📍 Адрес магазина")
async def show_categories2(message: Message):
    await message.answer('Наш магазин находится по 📍адресу: ул. Цветочная, д. 1\nРаботает каждый день \nПн-Пт: 9:00 - 21:00 \nСб-Вс: 10:00 - 20:00 \nНомер телефона для связи с администратором цветочного магазина 87369874326', reply_markup=kb.shop_address)

# О магазине
@router_client.message(F.text == "О магазине ℹ️")
async def show_categories3(message: Message):
    # Создаем inline клавиатуру с кнопкой для перехода на сайт
    website_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Перейти на сайт", url="https://ваш-сайт.com")]
    ])
    
    # Отправляем сообщение с клавиатурой
    await message.answer(
        'Всю интересующую вас информацию можно узнать на нашем сайте:',
        reply_markup=website_kb
    )

#Корзина
@router_client.message(lambda message: message.text == "Корзина")
async def show_cart(message: types.Message, state: FSMContext):
    # Открываем асинхронную сессию с базой данных
    async with AsyncSessionLocal() as db:
        try:
            user_id = message.from_user.id

            # Запрос для получения товаров в корзине с загрузкой связанных букетов
            cart_query = (
                select(Cart)
                .where(Cart.user_id == user_id)
                .options(selectinload(Cart.bouquet))  # Загружаем связанные объекты Bouquet
            )
            cart_result = await db.execute(cart_query)
            cart_items = cart_result.scalars().all()

            # Если корзина пуста
            if not cart_items:
                await message.answer("Ваша корзина пуста.")
                return

            total_price = 0
            cart_text = hunderline("Ваша корзина:") + "\n\n"

            # Перебираем товары в корзине
            for item in cart_items:
                if item.bouquet:
                    # Получаем цену (уже float)
                    price = item.bouquet.price if item.bouquet.price is not None else 0
                    quantity = item.quantity if item.quantity is not None else 0

                    cart_text += (
                        f"{hbold(item.bouquet.name)} - {price} руб. x {quantity}\n"
                    )
                    total_price += price * quantity
                else:
                    cart_text += f"{hbold('Букет удален')} (ID: {item.bouquet_id})\n\n"

            # Добавляем итоговую стоимость
            cart_text += hunderline(f"Итого: {total_price} руб.")

            # Отправляем сообщение с содержимым корзины и клавиатурой
            await message.answer(
                cart_text,
                reply_markup=get_cart_keyboard(cart_items),
                parse_mode="HTML"
            )

            # Устанавливаем состояние выбора доставки
            await state.set_state(OrderState.choosing_delivery)

        except Exception as e:
            await message.answer(f"Произошла ошибка при загрузке корзины: {e}")

async def get_cart_data(user_id: int, db: AsyncSession):
    # Запрос для получения товаров в корзине с загрузкой связанных букетов
    cart_query = (
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(selectinload(Cart.bouquet))  # Загружаем связанные объекты Bouquet
    )
    cart_result = await db.execute(cart_query)
    cart_items = cart_result.scalars().all()

    # Если корзина пуста
    if not cart_items:
        return None, None

    total_price = 0
    cart_text = hunderline("Ваша корзина:") + "\n\n"

    # Перебираем товары в корзине
    for item in cart_items:
        if item.bouquet:
            # Получаем цену (уже float)
            price = item.bouquet.price if item.bouquet.price is not None else 0
            quantity = item.quantity if item.quantity is not None else 0

            cart_text += (
                f"{hbold(item.bouquet.name)} - {price} руб. x {quantity}\n"
            )
            total_price += price * quantity
        else:
            cart_text += f"{hbold('Букет удален')} (ID: {item.bouquet_id})\n\n"

    # Добавляем итоговую стоимость
    cart_text += hunderline(f"Итого: {total_price} руб.")

    return cart_text, get_cart_keyboard(cart_items)

# Оформление заказа
@router_client.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as db:
        try:
            user_id = callback.from_user.id

            # Проверяем, есть ли товары в корзине
            cart_query = (
                select(Cart)
                .where(Cart.user_id == user_id)
                .options(selectinload(Cart.bouquet))  # Загружаем связанные объекты Bouquet
            )
            cart_result = await db.execute(cart_query)
            cart_items = cart_result.scalars().all()

            # Если корзина пуста
            if not cart_items:
                await callback.answer("Ваша корзина пуста. Добавьте товары для оформления заказа.")
                return

            # Сохраняем данные корзины в состоянии
            await state.update_data(cart_items=cart_items)

            # Предлагаем выбрать способ доставки
            await callback.message.answer("Выберите способ доставки:", reply_markup=get_delivery_keyboard())
            await state.set_state(OrderState.choosing_delivery)

        except Exception as e:
            logger.error(f"Ошибка при оформлении заказа: {e}")
            await callback.answer("Произошла ошибка при оформлении заказа. Пожалуйста, попробуйте позже.")

@router_client.callback_query(F.data.startswith("increase_"))
async def increase_quantity(callback: CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as db:
        try:
            # Извлекаем bouquet_id из callback.data
            try:
                bouquet_id = int(callback.data.split("_")[1])
            except (IndexError, ValueError):
                await callback.answer("Некорректный формат данных.")
                return

            user_id = callback.from_user.id

            # Находим элемент корзины
            cart_item_query = select(Cart).where(
                Cart.user_id == user_id,
                Cart.bouquet_id == bouquet_id
            )
            cart_item_result = await db.execute(cart_item_query)
            cart_item = cart_item_result.scalars().first()

            if cart_item:
                # Увеличиваем количество на 1
                cart_item.quantity += 1
                await db.commit()

                # Получаем обновленный текст корзины и клавиатуру
                cart_text, cart_keyboard = await get_cart_data(user_id, db)

                if cart_text and cart_keyboard:
                    # Редактируем существующее сообщение
                    await callback.message.edit_text(
                        cart_text,
                        reply_markup=cart_keyboard,
                        parse_mode="HTML"
                    )
                else:
                    await callback.answer("Ваша корзина пуста.")
            else:
                await callback.answer("Элемент корзины не найден.")
        except Exception as e:
            logger.error(f"Ошибка в increase_quantity: {e}")
            await callback.answer(f"Произошла ошибка: {e}")
            
@router_client.callback_query(F.data.startswith("decrease_"))
async def decrease_quantity(callback: types.CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as db:
        try:
            bouquet_id = int(callback.data.split("_")[1])
            user_id = callback.from_user.id

            # Находим элемент корзины
            cart_item_query = select(Cart).where(
                Cart.user_id == user_id,
                Cart.bouquet_id == bouquet_id
            )
            cart_item_result = await db.execute(cart_item_query)
            cart_item = cart_item_result.scalars().first()

            if cart_item:
                if cart_item.quantity > 1:
                    # Уменьшаем количество на 1
                    cart_item.quantity -= 1
                else:
                    # Если количество равно 1, удаляем букет из корзины
                    await db.execute(
                        delete(Cart)
                        .where(Cart.user_id == user_id, Cart.bouquet_id == bouquet_id)
                    )
                await db.commit()

                # Получаем обновленный текст корзины и клавиатуру
                cart_text, cart_keyboard = await get_cart_data(user_id, db)

                if cart_text and cart_keyboard:
                    # Редактируем существующее сообщение
                    await callback.message.edit_text(
                        cart_text,
                        reply_markup=cart_keyboard,
                        parse_mode="HTML"
                    )
                else:
                    await callback.answer("Ваша корзина пуста.")
            else:
                await callback.answer("Элемент корзины не найден.")
        except Exception as e:
            await callback.answer(f"Произошла ошибка: {e}")

@router_client.callback_query(F.data.startswith("remove_"))
async def remove_from_cart(callback: CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as db:
        try:
            # Извлекаем bouquet_id из callback_data
            bouquet_id = int(callback.data.split("_")[1])
            user_id = callback.from_user.id

            # Удаляем букет из корзины
            await db.execute(
                delete(Cart)
                .where(Cart.user_id == user_id, Cart.bouquet_id == bouquet_id)
            )
            await db.commit()

            # Получаем обновленный текст корзины и клавиатуру
            cart_text, cart_keyboard = await get_cart_data(user_id, db)  # Используем get_cart_data вместо show_cart

            if cart_text and cart_keyboard:
                # Редактируем существующее сообщение
                await callback.message.edit_text(
                    cart_text,
                    reply_markup=cart_keyboard,
                    parse_mode="HTML"
                )
            else:
                # Если корзина пуста, отправляем новое сообщение
                await callback.message.edit_text("Ваша корзина пуста.")
        except Exception as e:
            await callback.answer(f"Произошла ошибка: {e}")

# Выбор доставки
@router_client.callback_query(F.data.startswith("delivery_"), OrderState.choosing_delivery)
async def choose_delivery(callback: CallbackQuery, state: FSMContext):
    # Получаем тип доставки из callback-данных
    delivery_type = callback.data.split("_")[1]  # delivery или pickup
    
    # Переводим на русский
    delivery_type_russian = {
        "delivery": "Доставка",
        "pickup": "Самовывоз"
    }.get(delivery_type, delivery_type)
    
    await state.update_data(delivery_type=delivery_type, delivery_type_russian=delivery_type_russian)

    # Уведомляем пользователя о выборе
    await callback.answer(f"Вы выбрали: {delivery_type_russian}")

    # Переходим к выбору оплаты
    await callback.message.answer("Выберите способ оплаты:", reply_markup=get_payment_keyboard())
    await state.set_state(OrderState.choosing_payment)

#     # Предлагаем выбрать способ оплаты
#     await callback.message.answer("Выберите способ оплаты:", reply_markup=get_payment_keyboard())
#     await state.set_state(OrderState.choosing_payment)

# @router_client.message(F.text == "Доставка")
# async def communication_with_administrator(message: Message):
#     await message.answer("Извините доставка временно не работает", reply_markup=kb.delivery_keyboard)

# @router_client.message(F.text == "Наличные")
# async def communication_with_administrator(message: Message):
#     await message.answer("Вы можете оплатить букет наличными в магазине", reply_markup=kb.menu)
    
# @router_client.message(F.text == "Карта")
# async def communication_with_administrator(message: Message):
#     await message.answer("Вы можете оплатить букет картой в магазине после получения", reply_markup=kb.menu)
    
# @router_client.message(F.text == "Перевод")
# async def communication_with_administrator(message: Message):
#     await message.answer("Вы можете оплатить букет переводом и скинуть чек", reply_markup=kb.menu)
    


# Выбор оплаты
@router_client.callback_query(F.data.startswith("payment_"), OrderState.choosing_payment)
async def choose_payment(callback: CallbackQuery, state: FSMContext, bot: Bot):
    payment_method = callback.data.split("_")[1]  # cash, card или transfer
    
    # Переводим на русский
    payment_method_russian = {
        "cash": "Наличные",
        "card": "Карта",
        "transfer": "Перевод"
    }.get(payment_method, payment_method)
    
    await state.update_data(payment_method=payment_method, payment_method_russian=payment_method_russian)

    # Получаем ВСЕ данные из состояния
    data = await state.get_data()
    cart_items = data["cart_items"]
    delivery_type = data["delivery_type"]
    delivery_type_russian = data["delivery_type_russian"]
    payment_method = data["payment_method"]

    # Рассчитываем общую стоимость
    total_price = sum(
        item.bouquet.price * item.quantity 
        for item in cart_items 
        if item.bouquet and item.bouquet.price is not None
    )

    # Формируем текст заказа
    order_text = "Ваш заказ:\n\n"
    for item in cart_items:
        if item.bouquet:
            order_text += (
                f"{hbold(item.bouquet.name)} - {item.bouquet.price} руб. x {item.quantity}\n"
            )
        else:
            order_text += f"{hbold('Букет удален')} (ID: {item.bouquet_id})\n"

    order_text += hunderline(f"Итого: {total_price} руб.")
    order_text += f"\nСпособ доставки: {delivery_type_russian}"
    order_text += f"\nСпособ оплаты: {payment_method_russian}"

    # Отправляем пользователю подтверждение заказа
    await callback.message.answer(
        order_text,
        parse_mode="HTML"
    )

    # Сохраняем заказ в базу данных
    async with AsyncSessionLocal() as db:
        try:
            # Создаем новый заказ
            new_order = Order(
                user_id=callback.from_user.id,
                total_price=total_price,
                delivery_type=delivery_type,
                payment_method=payment_method,
                status="Принят"
            )
            db.add(new_order)
            await db.commit()
            await db.refresh(new_order)
            order_id = new_order.order_id

            # Сохраняем товары в заказе
            for item in cart_items:
                if item.bouquet:
                    order_item = OrderItem(
                        order_id=order_id,
                        bouquet_id=item.bouquet_id,
                        quantity=item.quantity,
                        price=item.bouquet.price
                    )
                    db.add(order_item)
            await db.commit()

            # Очищаем корзину
            await db.execute(delete(Cart).where(Cart.user_id == callback.from_user.id))
            await db.commit()

            # Получаем пользователя из БД для номера телефона
            user_query = await db.execute(
                select(User).where(User.user_id == callback.from_user.id))
            user = user_query.scalars().first()

            # Формируем сообщение для администратора
            admin_message = (
                f"🛒 *Новый заказ!* №{order_id}\n\n"
                f"👤 *Клиент:* {callback.from_user.full_name} "
                f"(@{callback.from_user.username or 'нет username'})\n"
                f"📞 *Телефон:* {user.phone if user and user.phone else 'не указан'}\n"
                f"📅 *Дата заказа:* {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
                f"📦 *Состав заказа:*\n"
            )
            
            for item in cart_items:
                if item.bouquet:
                    admin_message += f"  - {item.bouquet.name} x{item.quantity} = {item.bouquet.price * item.quantity} руб.\n"
            
            admin_message += (
                f"\n💰 *Итого:* {total_price} руб.\n"
                f"🚚 *Доставка:* {delivery_type_russian}\n"
                f"💳 *Оплата:* {payment_method_russian}\n\n"
                f"🆔 *ID заказа:* {order_id}"
            )

            # Отправляем уведомление администратору
            try:
                if ADMIN_CHAT_ID:
                    await bot.send_message(
                        chat_id=ADMIN_CHAT_ID,
                        text=admin_message,
                        parse_mode="Markdown"
                    )
                else:
                    logger.warning("ADMIN_CHAT_ID не установлен, уведомление не отправлено")
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления администратору: {e}")

        except Exception as e:
            logger.error(f"Ошибка при сохранении заказа: {e}")
            await callback.answer("Произошла ошибка при оформлении заказа. Пожалуйста, попробуйте позже.")
            return

    # Уведомляем пользователя об успешном оформлении
    await callback.answer("Заказ успешно оформлен! С вами свяжется администратор.")

    # Очищаем состояние
    await state.clear()

@router_client.message(F.text == "Связь с администратором")
async def communication_with_administrator(message: Message):
    await message.answer("Выберите способ связи с администратором", reply_markup=kb.admin_contact)

@router_client.message(F.text == "Позвонить")
async def call(message: types.Message, state: FSMContext):
    await message.answer("Вы можете связаться с администратором позвонив на номер +723569227455", reply_markup=kb.contact_as)

@router_client.message(F.text == "В чате")
async def In_chat(message: types.Message, state: FSMContext):
    await message.answer("Напишите вашу претензию @Sertaw", reply_markup=kb.contact_as)

# Сайт
@router_client.message(F.text == "Сайт")
async def Web_site(message: types.Message, state: FSMContext):
    await message.answer("Нажмите на ссылку ниже чтобы перейти на наш сайт", reply_markup=Website())

# YouTube
@router_client.message(F.text == "YouTube")
async def You_Tube(message: types.Message, state: FSMContext):
    await message.answer("Нажмите на ссылку ниже чтобы перейти на наш YouTube канал", reply_markup=You_tube())

# @router_client.message()
# async def unknown_message(message: types.Message):
#     await message.answer("Я тебя не понимаю. Попробуй выбрать команду из меню.")

# Помощь
@router_client.message(F.text == "❓ Помощь" or Command(help))
async def show_help(message: Message):
    help_text = """
❓ *Помощь*

Выберите интересующий вас раздел:

📦 Доставка - условия доставки
💳 Оплата - способы оплаты
📝 Условия - условия работы
❓ FAQ - частые вопросы
    """
    
    await message.answer(help_text, reply_markup=help_keyboard)
    
# Контакты
@router_client.message(F.text == "📞 Контакты")
async def show_contacts(message: Message):
    contacts_text = """
📞 *Наши контакты*

📱 Телефон: +7 (123) 45-67-89
✉️ Email: flower@shop.com
📍 Адрес: ул. Цветочная, д. 1

⏰ Режим работы:
Пн-Пт: 9:00 - 21:00
Сб-Вс: 10:00 - 20:00

Выберите удобный способ связи:
    """
    
    await message.answer(contacts_text, reply_markup=kb.contacts)
    
# Функция для обработки нажатий на кнопки
@router_client.message(lambda message: message.text in ['📞 Позвонить', '✉️ Написать', '📱 WhatsApp', '📱 Telegram', '🔙 Главное меню'])
async def handle_buttons(message: types.Message):
    phone_number = "+1234567890"  # Замените на нужный номер телефона
    
    if message.text == '📞 Позвонить':
        await message.answer(f'Вы можите позвонить по номеру +7123456789', reply_markup=kb.menu)
    elif message.text == '📱 WhatsApp':
        await message.answer(f"Чтобы позвонить через WhatsApp, нажмите [здесь](https://wa.me/{phone_number}).", parse_mode='Markdown', reply_markup=kb.menu)
    elif message.text == '📱 Telegram':
        await message.answer(f"Чтобы позвонить через Telegram, нажмите [здесь](tg://user?id={phone_number}).", parse_mode='Markdown', reply_markup=kb.menu)
    elif message.text == 'Меню':
        await message.answer("Возвращаемся в меню...", reply_markup=kb.menu)
    elif message.text == '✉️ Написать':
        await message.answer("Вы можете написать нашему администратору @Group", reply_markup=kb.menu)
        
# Часто задаваемые вопросы
@router_client.message(F.text == "❓ Часто задаваемые вопросы" or F.text == '❓ FAQ')
async def You_Tube(message: types.Message, state: FSMContext):
    # Текст с часто задаваемыми вопросами
    faq_text = """
❓ <b>Часто задаваемые вопросы (FAQ)</b>

1. <b>Как сделать заказ?</b>
   - Выберите категорию букетов, добавьте понравившийся букет в корзину и оформите заказ.

2. <b>Какие способы оплаты доступны?</b>
   - Мы принимаем оплату картой онлайн и наличными при получении.

3. <b>Как узнать статус моего заказа?</b>
   - Отслеживайте статус заказа в разделе "Мои заказы".

4. <b>Можно ли изменить адрес доставки после оформления заказа?</b>
   - Да, если заказ еще не передан курьеру.

5. <b>Как отменить заказ?</b>
   - Отмена возможна до передачи заказа курьеру через раздел "Мои заказы".

6. <b>Есть ли доставка в мой город?</b>
   - Мы доставляем по всему [название города]. Для других городов уточняйте у нас.

7. <b>Сколько стоит доставка?</b>
   - Стоимость зависит от вашего местоположения и отображается при оформлении заказа.

8. <b>Можно ли заказать букет с индивидуальным дизайном?</b>
   - Да, свяжитесь с нами для обсуждения деталей.

9. <b>Как узнать о скидках и акциях?</b>
   - Актуальные акции отображаются в разделе "Акции".

10. <b>Что делать, если я получил поврежденный букет?</b>
    - Свяжитесь с нами, и мы решим проблему.

11. <b>Можно ли заказать доставку в ночное время?</b>
    - Да, мы работаем 24/7.

12. <b>Как оставить отзыв?</b>
    - Оставьте отзыв в разделе "Отзывы".

13. <b>Есть ли подарочные сертификаты?</b>
    - Да, вы можете приобрести их через чат-бот.

14. <b>Как связаться с поддержкой?</b>
    - Напишите нам в чат-бот или позвоните по номеру [номер телефона].

15. <b>Можно ли заказать доставку в тот же день?</b>
    - Да, если заказ оформлен до [время].

<b>Если у вас остались вопросы, напишите нам!</b>
    """

    # Отправляем текст с FAQ
    await message.answer(faq_text, reply_markup=kb.menu, parse_mode="HTML")    

# Доставка
@router_client.message(F.text == "📦 Доставка")
async def You_Tube(message: types.Message, state: FSMContext):
    delivery_text = """
📦 <b>Информация о доставке</b>

- Мы осуществляем доставку по всему городу [название города].
- Стоимость доставки зависит от вашего местоположения.
- Доставка в тот же день возможна при заказе до [время].
- Вы можете отслеживать статус заказа в разделе "Мои заказы".

<b>Если у вас есть вопросы, свяжитесь с нами!</b>
    """
    await message.answer(delivery_text, reply_markup=kb.menu, parse_mode="HTML")

# Оплата
@router_client.message(F.text == "💳 Оплата")
async def You_Tube(message: types.Message, state: FSMContext):
    payment_text = """
💳 <b>Информация об оплате</b>

- Мы принимаем оплату картой онлайн.
- Также доступна оплата наличными при получении заказа.
- После оплаты вы получите чек на указанную почту.

<b>Если у вас возникли проблемы с оплатой, свяжитесь с нами!</b>
    """
    await message.answer(payment_text, reply_markup=kb.menu, parse_mode="HTML")

# Поддержка
@router_client.message(F.text == "📞 Поддержка")
async def You_Tube(message: types.Message, state: FSMContext):
    support_text = """
📞 <b>Служба поддержки</b>

- Мы всегда готовы помочь! Свяжитесь с нами:
  - Телефон: [номер телефона]
  - Email: [email]
  - Чат-бот: напишите нам здесь.

<b>Работаем круглосуточно!</b>
    """
    await message.answer(support_text, reply_markup=kb.menu, parse_mode="HTML")
    
# Условия
@router_client.message(F.text == "📝 Условия")
async def You_Tube(message: types.Message, state: FSMContext):
    terms_text = """
📝 <b>Условия заказа</b>

- Заказы принимаются круглосуточно.
- Доставка осуществляется в согласованные с вами сроки.
- Вы можете отменить заказ до передачи его курьеру.
- При получении поврежденного букета свяжитесь с нами для решения проблемы.

<b>Спасибо, что выбираете нас!</b>
    """
    await message.answer(terms_text, reply_markup=kb.menu, parse_mode="HTML")