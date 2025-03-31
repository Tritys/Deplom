from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, delete, update, func
from database.db import User, Category, Bouquet, Cart, Order, Promotion, OrderItem, get_admin_orders, update_order_status, AsyncSessionLocal
from database.db import AsyncSession
from sqlalchemy.future import select
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import joinedload
from keyboard.keyboard_admin import (
    admin_bouquets_kb, admin_promotions_kb,
    main_admin, profile_admin, get_categories_keyboard, get_orders_menu_keyboard
)

from aiogram.enums import ParseMode
from aiogram import Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import find_dotenv, load_dotenv, dotenv_values
import os
from aiogram.filters.base import Filter
from aiogram.filters.state import StateFilter
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
load_dotenv(find_dotenv())
import keyboard.keyboard_admin as kb_admin

router_admin = Router()

ADMIN_ID1 = int(os.getenv("ADMIN_IDS"))

# Фильтр для проверки прав администратора
class IsAdminFilter(Filter):
    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id == ADMIN_ID1

# Состояния для FSM
class AdminStates(StatesGroup):
    
    AddBouquetID = State()
    AddBouquetName  = State()
    AddBouquetCategory = State()
    AddBouquetPrice  = State()
    AddBouquetDescription  = State()
    AddBouquetImageURL  = State()
    
    EditBouquetID = State()
    EditBouquetName = State()
    EditBouquetPrice = State()
    EditBouquetDescription = State()
    EditBouquetImageURL = State()
    
    DeleteBouquet = State()
    
    AddPromotionTitle = State()
    AddPromotionDescription = State()
    AddPromotionDiscount = State()
    AddPromotionStartDate = State()
    AddPromotionEndDate = State()
    
    EditPromotionID = State()
    EditPromotionTitle = State()
    EditPromotionDescription = State()
    EditPromotionDiscount = State()
    EditPromotionStartDate = State()
    EditPromotionEndDate = State()
        
    DeletePromotionID = State()
    
    WaitingForStatus = State()  # Ожидание ввода нового статуса
    SearchOrderById = State()
    
# Команда /moderator
@router_admin.message(Command('moderators'))
async def process_moderator(message: types.Message):
    await message.answer("Добро пожаловать администратор!", reply_markup=kb_admin.main_admin)

# Меню
@router_admin.message(F.text == "меню")
async def process_menu(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать администратор!", reply_markup=kb_admin.main_admin)

# Профиль
@router_admin.message(F.text == "👤 Профиль")
async def show_profile(message: types.Message):
    async with AsyncSessionLocal() as db:
        user_id = message.from_user.id
        query = select(User).where(User.user_id == user_id)
        result = await db.execute(query)
        user = result.scalars().first()

        if user:
            await message.answer(
                f"Ваш профиль:\n"
                f"Ваш ID: {user.user_id}\n"
                f"Никнейм: {user.username}\n"
                f"Имя: {user.first_name}\n"
                f"Номер телефона: {user.phone}\n",
                reply_markup=kb_admin.profile_admin,
            )
        else:
            await message.answer("Профиль не найден. Пожалуйста, пройдите регистрацию, используя команду /start")

@router_admin.message(F.text == '💐 Букеты')
async def add_bouquet(message: types.Message, state: FSMContext):
    await state.clear()  # Очищаем состояние
    await message.answer("Добавление, изменение и удаление букетов:", reply_markup=admin_bouquets_kb())

# Команда для добавления нового букета
@router_admin.callback_query(F.data == "add_bouquet")
async def add_bouquet_start(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()  # Очищаем состояние
    await callback.message.answer("Введите ID букета:")
    await state.set_state(AdminStates.AddBouquetID)
    
# Команда для добавления нового букета
@router_admin.callback_query(F.data == "add_bouquet")
async def add_bouquet_start(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()  # Очищаем состояние
    await callback.message.answer("Введите ID букета:")
    await state.set_state(AdminStates.AddBouquetID)

# Обработчик для ввода ID букета при добавлении
@router_admin.message(StateFilter(AdminStates.AddBouquetID))
async def add_bouquet_id(message: types.Message, state: FSMContext):
    try:
        bouquet_id = int(message.text)  # Прямое преобразование с обработкой ошибок
    except ValueError:
        await message.answer("❌ Ошибка: ID должен быть целым числом. Пример: 123")
        return

    # Проверка существования ID
    async with AsyncSessionLocal() as db:
        existing_bouquet = await db.execute(select(Bouquet).where(Bouquet.bouquet_id == bouquet_id))
        if existing_bouquet.scalars().first():
            await message.answer("⚠️ Букет с таким ID уже существует.")
            return

    await state.update_data(bouquet_id=bouquet_id)
    await message.answer("Введите название букета:")
    await state.set_state(AdminStates.AddBouquetName)

# Обработчик для ввода названия букета
@router_admin.message(StateFilter(AdminStates.AddBouquetName))
async def add_bouquet_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    # Получаем клавиатуру с категориями
    keyboard = await get_categories_keyboard()
    if not keyboard:
        await message.answer("Категории не найдены. Сначала добавьте категорию.")
        return

    await message.answer("Выберите категорию:", reply_markup=keyboard)
    await state.set_state(AdminStates.AddBouquetCategory)

# Обработчик для выбора категории
@router_admin.callback_query(F.data.startswith("category_"))
async def process_category_selection(callback: types.CallbackQuery, state: FSMContext):
    try:
        category_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.message.answer("Ошибка при выборе категории. Попробуйте снова.")
        return  # Извлекаем ID категории
    await state.update_data(category_id=category_id)
    await callback.message.answer("Введите цену букета:")
    await state.set_state(AdminStates.AddBouquetPrice)

@router_admin.message(StateFilter(AdminStates.AddBouquetPrice))
async def add_bouquet_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)  # Пытаемся преобразовать в число
        await state.update_data(price=price)
        await message.answer("Введите описание букета:")
        await state.set_state(AdminStates.AddBouquetDescription)
    except ValueError:
        logger.error(f"Ошибка при вводе цены: {message.text}")
        await message.answer("Цена должна быть числом. Попробуйте снова или введите /cancel для отмены.")

@router_admin.message(StateFilter(AdminStates.AddBouquetDescription))
async def add_bouquet_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите URL изображения букета: ")
    await state.set_state(AdminStates.AddBouquetImageURL)

@router_admin.message(StateFilter(AdminStates.AddBouquetImageURL))
async def add_bouquet_image_url(message: types.Message, state: FSMContext):
    if not message.text.startswith("http"):
        await message.answer("URL должен начинаться с 'http'. Попробуйте снова.")
        return

    await state.update_data(image_url=message.text)
    data = await state.get_data()

    async with AsyncSessionLocal() as db:
        new_bouquet = Bouquet(
            category_id=data.get("category_id"),
            name=data["name"],
            price=data["price"],
            description=data["description"],
            image_url=data["image_url"]
        )
        db.add(new_bouquet)
        await db.commit()

    await message.answer("Букет успешно добавлен!")
    await state.set_state(None)

@router_admin.message(Command("cancel"))
async def cancel_operation(message: types.Message, state: FSMContext):
    # Очищаем состояние
    await state.clear()
    
    # Отправляем сообщение об отмене
    await message.answer("Операция отменена.", reply_markup=kb_admin.main_admin)

# Команда для изменения букета
@router_admin.callback_query(F.data == "edit_bouquet")
async def edit_bouquet_start(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()  # Очищаем состояние
    await callback.message.answer("Введите ID букета, который хотите изменить:")
    await state.set_state(AdminStates.EditBouquetID)

@router_admin.message(StateFilter(AdminStates.EditBouquetID))
async def edit_bouquet_id(message: types.Message, state: FSMContext):
    try:
        bouquet_id = int(message.text)  # Пытаемся преобразовать в число
        logger.info(f"Пользователь ввёл ID: {bouquet_id}")

        # Проверяем, существует ли букет с таким ID
        async with AsyncSessionLocal() as db:
            existing_bouquet = await db.execute(select(Bouquet).where(Bouquet.bouquet_id == bouquet_id))
            existing_bouquet = existing_bouquet.scalars().first()

            if not existing_bouquet:
                await message.answer("Букет с таким ID не найден. Попробуйте снова.")
                return

        # Сохраняем ID букета в состоянии
        await state.update_data(bouquet_id=bouquet_id)
        await message.answer("Введите новое название букета:")
        await state.set_state(AdminStates.EditBouquetName)

    except ValueError:
        logger.error(f"Ошибка при вводе ID: {message.text}")
        await message.answer("ID должен быть числом. Попробуйте снова.")

@router_admin.message(StateFilter(AdminStates.EditBouquetName))
async def edit_bouquet_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите новую цену букета:")
    await state.set_state(AdminStates.EditBouquetPrice)

@router_admin.message(StateFilter(AdminStates.EditBouquetPrice))
async def edit_bouquet_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await message.answer("Введите новое описание букета:")
        await state.set_state(AdminStates.EditBouquetDescription)
    except ValueError:
        await message.answer("Цена должна быть числом. Попробуйте снова.")

@router_admin.message(StateFilter(AdminStates.EditBouquetDescription))
async def edit_bouquet_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите новый URL изображения букета:")
    await state.set_state(AdminStates.EditBouquetImageURL)

@router_admin.message(StateFilter(AdminStates.EditBouquetImageURL))
async def edit_bouquet_image_url(message: types.Message, state: FSMContext):    
    if not message.text.startswith("http"):
        await message.answer("URL должен начинаться с 'http'. Попробуйте снова.")
        return

    await state.update_data(image_url=message.text)
    data = await state.get_data()

    async with AsyncSessionLocal() as db:
        await db.execute(
            update(Bouquet)
            .where(Bouquet.bouquet_id == data["bouquet_id"])
            .values(
                name=data["name"],
                price=data["price"],
                description=data["description"],
                image_url=data["image_url"]
            )
        )
        await db.commit()

    await message.answer("Букет успешно изменен!")
    await state.set_state(None)

# Команда для удаления букета
@router_admin.callback_query(F.data == "delete_bouquet")
async def delete_bouquet_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ID букета, который хотите удалить:")
    await state.set_state(AdminStates.DeleteBouquet)

@router_admin.message(StateFilter(AdminStates.DeleteBouquet))
async def delete_bouquet_id(message: types.Message, state: FSMContext):
    # Проверяем, если пользователь ввёл команду или текст, который не является числом
    if not message.text.isdigit():
        await state.clear()  # Очищаем состояние
        await message.answer("Операция отменена. Вы ввели нечисловое значение.", reply_markup=admin_bouquets_kb())
        return

    try:
        bouquet_id = int(message.text)
        async with AsyncSessionLocal() as db:
            existing_bouquet = await db.execute(select(Bouquet).where(Bouquet.bouquet_id == bouquet_id))
            existing_bouquet = existing_bouquet.scalars().first()

            if not existing_bouquet:
                await message.answer("Букет с таким ID не найден.")
                return 

            await db.execute(
                delete(Bouquet)
                .where(Bouquet.bouquet_id == bouquet_id)
            )
            await db.commit()

        await message.answer("Букет успешно удален!")
        await state.set_state(None)  # Очищаем состояние после успешного удаления
    except ValueError:
        await message.answer("ID должен быть числом. Попробуйте снова.")

@router_admin.message(F.text == '🎉 Акции')
async def add_promotion(message: types.Message, state: FSMContext):
    await state.clear()  # Очищаем состояние
    await message.answer("Добавление, изменение и удаление акций:", reply_markup=admin_promotions_kb())
    
# Команда для добавления акции
@router_admin.callback_query(F.data == "add_promotion")
async def add_promotion_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название акции:")
    await state.set_state(AdminStates.AddPromotionTitle)

@router_admin.message(StateFilter(AdminStates.AddPromotionTitle))
async def add_promotion_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание акции:")
    await state.set_state(AdminStates.AddPromotionDescription)

@router_admin.message(StateFilter(AdminStates.AddPromotionDescription))
async def add_promotion_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите скидку (в процентах):")
    await state.set_state(AdminStates.AddPromotionDiscount)

@router_admin.message(StateFilter(AdminStates.AddPromotionDiscount))
async def add_promotion_discount(message: types.Message, state: FSMContext):
    try:
        discount = float(message.text)
        await state.update_data(discount=discount)
        await message.answer("Введите дату начала акции (в формате ГГГГ-ММ-ДД):")
        await state.set_state(AdminStates.AddPromotionStartDate)
    except ValueError:
        await message.answer("Скидка должна быть числом. Попробуйте снова.")

@router_admin.message(StateFilter(AdminStates.AddPromotionStartDate))
async def add_promotion_start_date(message: types.Message, state: FSMContext):
    try:
        # Проверяем, что дата введена в правильном формате
        datetime.strptime(message.text, "%Y-%m-%d")
        await state.update_data(start_date=message.text)
        await message.answer("Введите дату окончания акции (в формате ГГГГ-ММ-ДД):")
        await state.set_state(AdminStates.AddPromotionEndDate)
    except ValueError:
        await message.answer("Неверный формат даты. Введите дату в формате ГГГГ-ММ-ДД.")

@router_admin.message(StateFilter(AdminStates.AddPromotionEndDate))
async def add_promotion_end_date(message: types.Message, state: FSMContext):
    try:
        # Проверяем, что дата введена в правильном формате
        datetime.strptime(message.text, "%Y-%m-%d")
        await state.update_data(end_date=message.text)
        data = await state.get_data()

        async with AsyncSessionLocal() as db:
            new_promotion = Promotion(
                title=data["title"],
                description=data["description"],
                discount=data["discount"],
                start_date=data["start_date"],
                end_date=data["end_date"]
            )
            db.add(new_promotion)
            await db.commit()

        await message.answer("Акция успешно добавлена!")
        await state.set_state(None)
    except ValueError:
        await message.answer("Неверный формат даты. Введите дату в формате ГГГГ-ММ-ДД.")

# Команда для изменения акций
@router_admin.callback_query(F.data == "edit_promotion")
async def edit_promotion_start(message: types.Message, state: FSMContext):
    await message.answer("Введите ID акции для изменения:")
    await state.set_state(AdminStates.EditPromotionID)

@router_admin.message(StateFilter(AdminStates.EditPromotionID))
async def edit_promotion_id(message: types.Message, state: FSMContext):
    try:
        promotion_id = int(message.text)
        async with AsyncSessionLocal() as db:
            promotion = await db.execute(select(Promotion).where(Promotion.promotion_id == promotion_id))
            promotion = promotion.scalars().first()
            if not promotion:
                await message.answer("Акция с таким ID не найдена. Попробуйте снова.")
                return

            await state.update_data(promotion_id=promotion_id)
            await state.update_data(title=promotion.title)
            await state.update_data(description=promotion.description)
            await state.update_data(discount=promotion.discount)
            await state.update_data(start_date=promotion.start_date)
            await state.update_data(end_date=promotion.end_date)

            await message.answer("Акция найдена. Введите новое название акции (или оставьте пустым для сохранения):")
            await state.set_state(AdminStates.EditPromotionTitle)
    except ValueError:
        await message.answer("Ошибка: ID акции должен быть числом. Попробуйте снова.")

@router_admin.message(StateFilter(AdminStates.EditPromotionTitle))
async def edit_promotion_title(message: types.Message, state: FSMContext):
    if message.text.strip():
        await state.update_data(title=message.text)
        await message.answer("Название акции обновлено.")
    else:
        await message.answer("Название акции осталось без изменений.")
    await message.answer("Введите новое описание акции (или оставьте пустым для сохранения):")
    await state.set_state(AdminStates.EditPromotionDescription)

@router_admin.message(StateFilter(AdminStates.EditPromotionDescription))
async def edit_promotion_description(message: types.Message, state: FSMContext):
    if message.text.strip():
        await state.update_data(description=message.text)
    await message.answer("Введите новую скидку (или оставьте пустым для сохранения):")
    await state.set_state(AdminStates.EditPromotionDiscount)

@router_admin.message(StateFilter(AdminStates.EditPromotionDiscount))
async def edit_promotion_discount(message: types.Message, state: FSMContext):
    if message.text.strip():
        try:
            discount = float(message.text)
            await state.update_data(discount=discount)
        except ValueError:
            await message.answer("Ошибка: Скидка должна быть числом. Используется старая скидка.")

    await message.answer("Введите новую дату начала акции (в формате ГГГГ-ММ-ДД, или оставьте пустым для сохранения):")
    await state.set_state(AdminStates.EditPromotionStartDate)

@router_admin.message(StateFilter(AdminStates.EditPromotionStartDate))
async def edit_promotion_start_date(message: types.Message, state: FSMContext):
    if message.text.strip():
        await state.update_data(start_date=message.text)
    await message.answer("Введите новую дату окончания акции (в формате ГГГГ-ММ-ДД, или оставьте пустым для сохранения):")
    await state.set_state(AdminStates.EditPromotionEndDate)

@router_admin.message(StateFilter(AdminStates.EditPromotionEndDate))
async def edit_promotion_end_date(message: types.Message, state: FSMContext):
    if message.text.strip():
        await state.update_data(end_date=message.text)

    data = await state.get_data()

    async with AsyncSessionLocal() as db:
        promotion = await db.execute(select(Promotion).where(Promotion.promotion_id == data["promotion_id"]))
        promotion = promotion.scalars().first()

        promotion.title = data["title"] if data["title"] else promotion.title
        promotion.description = data["description"] if data["description"] else promotion.description
        promotion.discount = data["discount"] if data["discount"] else promotion.discount
        promotion.start_date = data["start_date"] if data["start_date"] else promotion.start_date
        promotion.end_date = data["end_date"] if data["end_date"] else promotion.end_date

        await db.commit()

    await message.answer("Акция успешно изменена!")
    await state.set_state(None)

# Команда для удаления акций
@router_admin.callback_query(F.data == "delete_promotion")
async def delete_promotion_start(message: types.Message, state: FSMContext):
    await message.answer("Введите ID акции для удаления:")
    await state.set_state(AdminStates.DeletePromotionID)

@router_admin.message(StateFilter(AdminStates.DeletePromotionID))
async def delete_promotion_id(message: types.Message, state: FSMContext):
    try:
        promotion_id = int(message.text)
        async with AsyncSessionLocal() as db:
            promotion = await db.execute(select(Promotion).where(Promotion.promotion_id == promotion_id))
            promotion = promotion.scalars().first()
            if not promotion:
                await message.answer("Акция с таким ID не найдена. Попробуйте снова.")
                return

            await db.delete(promotion)
            await db.commit()

        await message.answer("Акция успешно удалена!")
        await state.set_state(None)
    except ValueError:
        await message.answer("Ошибка: ID акции должен быть числом. Попробуйте снова.")

# Обработчик для кнопки "Активные акции"
@router_admin.callback_query(F.data == "active_promotions")
async def view_active_promotions(callback: types.CallbackQuery):
    async with AsyncSessionLocal() as db:
        # Получаем текущую дату
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Запрос активных акций
        promotions = await db.execute(
            select(Promotion)
            .where(Promotion.start_date <= current_date)
            .where(Promotion.end_date >= current_date)
        )
        promotions = promotions.scalars().all()

        if not promotions:
            await callback.message.answer("🎁 Активных акций нет.")
            return

        # Формируем сообщение с активными акциями
        response = "🎁 <b>Активные акции:</b>\n\n"
        for promotion in promotions:
            response += (
                f"🔹 <b>{promotion.title}</b>\n"
                f"📝 Описание: {promotion.description}\n"
                f"💸 Скидка: {promotion.discount}%\n"
                f"📅 Действует с {promotion.start_date} по {promotion.end_date}\n\n"
            )

        await callback.message.answer(response, parse_mode=ParseMode.HTML)


# Функция для получения заказов
async def get_admin_orders(db: AsyncSession):
    result = await db.execute(
        select(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.bouquet))  # Загружаем связанные данные
    )
    return result.unique().scalars().all()

# Функция для форматирования даты
def format_date(date_obj):
    return date_obj.strftime("%d.%m.%Y %H:%M")

# Функция для обновления статуса заказа
async def update_order_status(db: AsyncSession, order_id: int, new_status: str):
    order = await db.execute(
        select(Order)
        .where(Order.order_id == order_id)
    )
    order = order.scalars().first()
    if order:
        order.status = new_status
        await db.commit()
        await db.refresh(order)
        return order
    return None

# Заказы
@router_admin.message(F.text == '📦 Заказы')
async def show_orders_menu(message: types.Message):
    await message.answer("Меню управления заказами:", reply_markup=get_orders_menu_keyboard())
    

    
@router_admin.callback_query(F.data == "view_orders")
async def view_orders(callback: types.CallbackQuery):
    async with AsyncSessionLocal() as db:
        orders = await get_admin_orders(db)
        if orders:
            for order in orders:
                items_info = "Товары:\n"
                if order.items:
                    for item in order.items:
                        items_info += (
                            f"🔹 {item.bouquet.name} (x{item.quantity}) - {item.price} руб.\n"
                        )
                else:
                    items_info += "Нет товаров.\n"

                await callback.message.answer(
                    f"Заказ №{order.order_id}\n"
                    f"Пользователь: {order.user_id}\n"
                    f"Сумма: {order.total_price} руб.\n"
                    f"Тип доставки: {order.delivery_type}\n"
                    f"Статус: {order.status}\n"
                    f"Дата создания: {format_date(order.created_at)}\n"
                    f"{items_info}"
                )
        else:
            await callback.message.answer("Нет заказов.")
            
@router_admin.callback_query(F.data == "search_order_by_id")
async def search_order_by_id(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ID заказа для поиска:")
    await state.set_state(AdminStates.SearchOrderById)

@router_admin.message(AdminStates.SearchOrderById, F.text)
async def process_search_order_by_id(message: types.Message, state: FSMContext):
    try:
        order_id = int(message.text)
        async with AsyncSessionLocal() as db:
            order = await db.execute(
                select(Order)
                .options(joinedload(Order.items).joinedload(OrderItem.bouquet))
                .where(Order.order_id == order_id)
            )
            order = order.unique().scalars().first()

            if order:
                items_info = "Товары:\n"
                if order.items:
                    for item in order.items:
                        items_info += (
                            f"🔹 {item.bouquet.name} (x{item.quantity}) - {item.price} руб.\n"
                        )
                else:
                    items_info += "Нет товаров.\n"

                await message.answer(
                    f"Заказ №{order.order_id}\n"
                    f"Пользователь: {order.user_id}\n"
                    f"Сумма: {order.total_price} руб.\n"
                    f"Тип доставки: {order.delivery_type}\n"
                    f"Статус: {order.status}\n"
                    f"Дата создания: {format_date(order.created_at)}\n"
                    f"{items_info}"
                )
            else:
                await message.answer("Заказ с таким ID не найден.")
    except ValueError:
        await message.answer("ID заказа должен быть числом. Попробуйте снова.")
    await state.clear()
            
@router_admin.callback_query(F.data == "change_order_status")
async def change_order_status(callback: types.CallbackQuery):
    async with AsyncSessionLocal() as db:
        orders = await get_admin_orders(db)
        
        # Создаем список кнопок для клавиатуры
        buttons = []
        for order in orders:
            buttons.append([InlineKeyboardButton(
                text=f"Заказ №{order.order_id}",
                callback_data=f"change_order_status_{order.order_id}"
            )])
        
        # Создаем клавиатуру с кнопками
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await callback.message.answer("Выберите заказ для изменения статуса:", reply_markup=keyboard)

@router_admin.callback_query(F.data.startswith("change_order_status_"))
async def process_change_order_status(callback: types.CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split("_")[-1])
    await state.update_data(order_id=order_id)
    await state.set_state(AdminStates.WaitingForStatus)
    await callback.message.answer("Введите новый статус заказа (например, 'выполнен' или 'отменен'):")

@router_admin.message(AdminStates.WaitingForStatus, F.text)
async def save_changed_order_status(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_id = data.get('order_id')
    if order_id is None:
        await message.answer("Ошибка: не удалось найти ID заказа. Попробуйте снова.")
        return

    new_status = message.text
    async with AsyncSessionLocal() as db:
        order = await update_order_status(db, order_id, new_status)
        if order:
            await message.answer(f"Статус заказа №{order_id} успешно изменен на '{new_status}'.")
        else:
            await message.answer("Заказ не найден.")

    await state.clear()



# Обработчик для необработанных callback-запросов
@router_admin.callback_query()
async def handle_unprocessed_callbacks(callback: types.CallbackQuery):
    await callback.answer("Действие не распознано.")

# Обработчик для нераспознанных команд
@router_admin.message()
async def handle_unknown_commands(message: types.Message):
    await message.answer("Команда не распознана. Введите /help для списка доступных команд.")








# # Статистика
# @router_admin.message(F.text == "📊 Статистика")
# async def show_statistics(message: types.Message):
#     # Проверка, что команду вызвал администратор
#     if message.from_user.id != ADMIN_ID1:
#         return
    
#     async with AsyncSessionLocal() as session:
#         try:
#             # Общее количество заказов
#             total_orders = await session.execute(select(func.count(Order.order_id)))
#             total_orders = total_orders.scalar()
            
#             # Общая сумма продаж
#             total_sales = await session.execute(select(func.sum(Order.total_price)))
#             total_sales = total_sales.scalar() or 0  # Если сумма NULL, возвращаем 0
            
#             # Количество пользователей
#             total_users = await session.execute(select(func.count(User.user_id)))
#             total_users = total_users.scalar()
            
#             # Статистика за последние 24 часа
#             yesterday = datetime.now() - timedelta(days=1)
#             recent_orders = await session.execute(
#                 select(func.count(Order.order_id))
#                 .where(Order.created_at >= yesterday)
#             )
#             recent_orders = recent_orders.scalar()
            
#             # Формируем текст сообщения
#             stats_text = f"""
# 📊 *Общая статистика магазина*

# 📦 Всего заказов: {total_orders}
# 💰 Общая сумма продаж: {total_sales:.2f}₽
# 👥 Количество пользователей: {total_users}
# 🕒 Заказов за 24 часа: {recent_orders}
#             """
            
#             # Отправляем сообщение с клавиатурой
#             await message.answer(stats_text, reply_markup=kb_admin.main1_admin)
        
#         except Exception as e:
#             # Логируем ошибку, если что-то пошло не так
#             logger.error(f"Ошибка при получении статистики: {e}")
#             await message.answer("Произошла ошибка при получении данных. Попробуйте позже.")

# # Управление пользователями
# @router_admin.message(F.text == "👥 Пользователи")
# async def manage_users(message: types.Message):
#     # Проверка, что команду вызвал администратор
#     if message.from_user.id != ADMIN_ID1:
#         return
    
#     async with AsyncSessionLocal() as session:
#         try:
#             # Получаем общее количество пользователей
#             total_users = await session.execute(select(func.count(User.user_id)))
#             total_users = total_users.scalar()
            
#             # Получаем количество активных пользователей
#             active_users = await session.execute(
#                 select(func.count(User.user_id))
#                 .where(User.is_active == True)
#             )
#             active_users = active_users.scalar()
            
#             # Формируем текст сообщения
#             users_text = f"""
# 👥 *Управление пользователями*

# 👤 Всего пользователей: {total_users}
# ✅ Активные: {active_users}
# ❌ Неактивные: {total_users - active_users}
#             """
            
#             # Отправляем сообщение с клавиатурой
#             await message.answer(users_text, reply_markup=kb_admin.main1_admin)
        
#         except Exception as e:
#             # Логируем ошибку, если что-то пошло не так
#             logger.error(f"Ошибка при получении статистики пользователей: {e}")
#             await message.answer("Произошла ошибка при получении данных. Попробуйте позже.")