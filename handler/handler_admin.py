from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from database.db import User, Category, Bouquet, Cart, Order, Promotion, get_admin_orders, update_order_status, AsyncSessionLocal
from database.db import AsyncSession
from sqlalchemy.future import select
from aiogram.fsm.state import State, StatesGroup
from keyboard.keyboard_admin import admin_bouquets_kb, admin_promotions_kb
from aiogram import Dispatcher

import logging
logger = logging.getLogger(__name__)

import keyboard.keyboard_admin as kb_admin
router_admin = Router()

# Команда /moderator
@router_admin.message(Command('moderator'))
async def process_moderator(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать администратор!", reply_markup=kb_admin.main_admin)

# Меню
@router_admin.message(F.text == "меню")
async def process_menu(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать администратор!", reply_markup=kb_admin.main_admin)

# Профиль
@router_admin.message(F.text == "профиль")
async def show_profile(message: types.Message):
    async with AsyncSessionLocal() as db:
        user_id = message.from_user.id

        # Асинхронный запрос к базе данных
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
                reply_markup=kb_admin.profile_admin,
            )
        else:
            await message.answer(
                "Профиль не найден. Пожалуйста, пройдите регистрацию, используя команду /start"
            )

# Букеты
@router_admin.message(F.text == 'Букеты')
async def process_bouquets(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать администратор!", reply_markup=admin_bouquets_kb())

class AddBouquetState(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()

@router_admin.callback_query(F.data == "add_bouquet")
async def add_bouquet(callback: types.CallbackQuery):
    logger.info("Обработчик 'add_bouquet' вызван.")
    try:
        await callback.message.answer("Введите название букета:")
    except Exception as e:
        logger.error(f"Ошибка в обработчике 'add_bouquet': {e}")

@router_admin.message(AddBouquetState.waiting_for_name)
async def process_bouquet_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание букета:")
    await state.set_state(AddBouquetState.waiting_for_description)

@router_admin.message(AddBouquetState.waiting_for_description)
async def process_bouquet_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите цену букета:")
    await state.set_state(AddBouquetState.waiting_for_price)

@router_admin.message(AddBouquetState.waiting_for_price)
async def process_bouquet_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
        data = await state.get_data()
        name = data.get("name")
        description = data.get("description")

        async with AsyncSessionLocal() as db:
            new_bouquet = Bouquet(name=name, description=description, price=price)
            db.add(new_bouquet)
            await db.commit()
            await message.answer(f"Букет '{name}' успешно добавлен!")
    except ValueError:
        await message.answer("Цена должна быть числом. Попробуйте снова.")
    finally:
        await state.clear()


# Удаление букета
@router_admin.callback_query(F.data == "delete_bouquet")
async def delete_bouquet(callback: types.CallbackQuery):
    async with AsyncSessionLocal() as db:
        query = select(Bouquet)
        result = await db.execute(query)
        bouquets = result.scalars().all()

        keyboard = InlineKeyboardMarkup(row_width=1)
        for bouquet in bouquets:
            keyboard.add(InlineKeyboardButton(bouquet.name, callback_data=f"delete_bouquet_{bouquet.bouquet_id}"))

        await callback.message.answer("Выберите букет для удаления:", reply_markup=keyboard)

# Подтверждение удаления букета
@router_admin.callback_query(F.data.startswith("delete_bouquet_"))
async def confirm_delete_bouquet(callback: types.CallbackQuery):
    bouquet_id = int(callback.data.split("_")[-1])
    async with AsyncSessionLocal() as db:
        query = select(Bouquet).where(Bouquet.bouquet_id == bouquet_id)
        result = await db.execute(query)
        bouquet = result.scalars().first()

        if bouquet:
            await db.delete(bouquet)
            await db.commit()
            await callback.message.answer(f"Букет '{bouquet.name}' удален.")
        else:
            await callback.message.answer("Букет не найден.")

# Изменение букета
@router_admin.callback_query(F.data == "edit_bouquet")
async def edit_bouquet(callback: types.CallbackQuery):
    async with AsyncSessionLocal() as db:
        query = select(Bouquet)
        result = await db.execute(query)
        bouquets = result.scalars().all()

        keyboard = InlineKeyboardMarkup(row_width=1)
        for bouquet in bouquets:
            keyboard.add(InlineKeyboardButton(bouquet.name, callback_data=f"edit_bouquet_{bouquet.bouquet_id}"))

        await callback.message.answer("Выберите букет для изменения:", reply_markup=keyboard)

@router_admin.callback_query(F.data.startswith("edit_bouquet_"))
async def process_edit_bouquet(callback: types.CallbackQuery, state: FSMContext):
    bouquet_id = int(callback.data.split("_")[-1])
    await state.update_data(bouquet_id=bouquet_id)  # Сохраняем ID букета в состоянии
    await callback.message.answer("Введите новое название букета:")

@router_admin.message(F.text)
async def save_edited_bouquet(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        if 'bouquet_id' not in data:
            logger.error("Ключ 'bouquet_id' отсутствует в состоянии.")
            await message.answer("Ошибка: ID букета не найден. Пожалуйста, начните процесс заново.")
            return

        bouquet_id = data['bouquet_id']
        new_name = message.text

        async with AsyncSessionLocal() as db:
            query = select(Bouquet).where(Bouquet.bouquet_id == bouquet_id)
            result = await db.execute(query)
            bouquet = result.scalars().first()

            if bouquet:
                bouquet.name = new_name
                await db.commit()
                await message.answer(f"Букет успешно изменен на '{new_name}'.")
            else:
                await message.answer("Букет не найден.")
        
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при изменении букета: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

# Акции
@router_admin.message(F.text == 'Акции_admin')
async def process_promotions(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать администратор!", reply_markup=admin_promotions_kb())

# Добавление акции
@router_admin.callback_query(F.data == "add_promotion")
async def add_promotion(callback: types.CallbackQuery):
    await callback.message.answer("Введите название акции:")

# Удаление акции
@router_admin.callback_query(F.data == "delete_promotion")
async def delete_promotion(callback: types.CallbackQuery):
    async with AsyncSessionLocal() as db:
        query = select(Promotion)
        result = await db.execute(query)
        promotions = result.scalars().all()

        keyboard = InlineKeyboardMarkup(row_width=1)
        for promotion in promotions:
            keyboard.add(InlineKeyboardButton(promotion.title, callback_data=f"delete_promotion_{promotion.promotion_id}"))

        await callback.message.answer("Выберите акцию для удаления:", reply_markup=keyboard)

# Подтверждение удаления акции
@router_admin.callback_query(F.data.startswith("delete_promotion_"))
async def confirm_delete_promotion(callback: types.CallbackQuery):
    promotion_id = int(callback.data.split("_")[-1])
    async with AsyncSessionLocal() as db:
        query = select(Promotion).where(Promotion.promotion_id == promotion_id)
        result = await db.execute(query)
        promotion = result.scalars().first()

        if promotion:
            await db.delete(promotion)
            await db.commit()
            await callback.message.answer(f"Акция '{promotion.title}' удалена.")
        else:
            await callback.message.answer("Акция не найдена.")

# Изменение акции
@router_admin.callback_query(F.data == "edit_promotion")
async def edit_promotion(callback: types.CallbackQuery):
    async with AsyncSessionLocal() as db:
        query = select(Promotion)
        result = await db.execute(query)
        promotions = result.scalars().all()

        keyboard = InlineKeyboardMarkup(row_width=1)
        for promotion in promotions:
            keyboard.add(InlineKeyboardButton(promotion.title, callback_data=f"edit_promotion_{promotion.promotion_id}"))

        await callback.message.answer("Выберите акцию для изменения:", reply_markup=keyboard)

@router_admin.callback_query(F.data.startswith("edit_promotion_"))
async def process_edit_promotion(callback: types.CallbackQuery, state: FSMContext):
    promotion_id = int(callback.data.split("_")[-1])
    await state.update_data(promotion_id=promotion_id)
    await callback.message.answer("Введите новое название акции:")

@router_admin.message(F.text)
async def save_edited_promotion(message: types.Message, state: FSMContext):
    data = await state.get_data()
    promotion_id = data['promotion_id']
    new_title = message.text

    async with AsyncSessionLocal() as db:
        query = select(Promotion).where(Promotion.promotion_id == promotion_id)
        result = await db.execute(query)
        promotion = result.scalars().first()

        if promotion:
            promotion.title = new_title
            await db.commit()
            await message.answer(f"Акция успешно изменена на '{new_title}'.")
        else:
            await message.answer("Акция не найдена.")
    await state.clear()


# Заказы
@router_admin.message(F.text == 'Заказы')
async def show_orders(message: types.Message):
    async with AsyncSessionLocal() as db:
        orders = await get_admin_orders(db)
        if orders:
            for order in orders:
                await message.answer(
                    f"Заказ №{order.order_id}\n"
                    f"Пользователь: {order.user_id}\n"
                    f"Сумма: {order.total_price}\n"
                    f"Тип доставки: {order.delivery_type}\n"
                    f"Статус: {order.status}"
                )
        else:
            await message.answer("Нет заказов.")

# Изменение статуса заказа
@router_admin.callback_query(F.data == "change_order_status")
async def change_order_status(callback: types.CallbackQuery):
    async with AsyncSessionLocal() as db:
        orders = await get_admin_orders(db)
        keyboard = InlineKeyboardMarkup(row_width=1)
        for order in orders:
            keyboard.add(InlineKeyboardButton(f"Заказ №{order.order_id}", callback_data=f"change_order_status_{order.order_id}"))

        await callback.message.answer("Выберите заказ для изменения статуса:", reply_markup=keyboard)

@router_admin.callback_query(F.data.startswith("change_order_status_"))
async def process_change_order_status(callback: types.CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split("_")[-1])
    await state.update_data(order_id=order_id)
    await callback.message.answer("Введите новый статус заказа (например, 'выполнен' или 'отменен'):")

@router_admin.message(F.text)
async def save_changed_order_status(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_id = data['order_id']
    new_status = message.text

    async with AsyncSessionLocal() as db:
        order = await update_order_status(db, order_id, new_status)
        if order:
            await message.answer(f"Статус заказа №{order_id} успешно изменен на '{new_status}'.")
        else:
            await message.answer("Заказ не найден.")
    await state.clear()

# Регистрация обработчиков
def register_handlers_admin(dp: Dispatcher):
    dp.include_router(router_admin)