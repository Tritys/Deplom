from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram import types
from database.db import AsyncSessionLocal
from database.models import Category
from sqlalchemy.future import select

main_admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='📦 Заказы'), KeyboardButton(text='👤 Профиль')],
    [KeyboardButton(text='💐 Букеты'), KeyboardButton(text='🎉 Акции')],
    [KeyboardButton(text='📊 Статистика'), KeyboardButton(text='👥 Пользователи')],
    # [KeyboardButton(text='⚙️ Настройки'), KeyboardButton(text='❓ Помощь')],
], resize_keyboard=True, input_field_placeholder='Выберите раздел админ-панели')


main1_admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='💐 Букеты'), KeyboardButton(text='👤 Профиль')],
    [KeyboardButton(text='🎉 Акции'), KeyboardButton(text='меню')],
], resize_keyboard=True, input_field_placeholder='Выберите раздел админ-панели')

def admin_bouquets_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        # [InlineKeyboardButton(text="➕ Добавить букет", callback_data="add_bouquet")],
        [InlineKeyboardButton(text="✏️ Изменить букет", callback_data="edit_bouquet")],
        [InlineKeyboardButton(text="❌ Удалить букет", callback_data="delete_bouquet")],
        # [InlineKeyboardButton(text="Отмена", callback_data="cancel")],
        # [InlineKeyboardButton(text="🏷️ Управление категориями", callback_data="manage_categories")],
        # [InlineKeyboardButton(text="🔄 Обновить наличие", callback_data="update_availability")],
        # [InlineKeyboardButton(text="📋 Список букетов", callback_data="list_bouquets")],
        # [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin_menu")]
    ])

def admin_promotions_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        # [InlineKeyboardButton(text="➕ Добавить акцию", callback_data="add_promotion")],
        [InlineKeyboardButton(text="✏️ Изменить акцию", callback_data="edit_promotion")],
        [InlineKeyboardButton(text="❌ Удалить акцию", callback_data="delete_promotion")],
        [InlineKeyboardButton(text="📅 Активные акции", callback_data="active_promotions")],
        # [InlineKeyboardButton(text="Отмена", callback_data="cancel")],
        # [InlineKeyboardButton(text="📊 Статистика акций", callback_data="promotion_stats")],
        # [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin_menu")]
    ])

# Профиль
profile_admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='💐 Букеты'), KeyboardButton(text='🎉 Акции')],
    [KeyboardButton(text='📦 Заказы'), KeyboardButton(text='меню')],
    # [KeyboardButton(text='🔙 Главное меню')]
], resize_keyboard=True, input_field_placeholder='Выберите действие')

# Функция для получения клавиатуры с категориями
async def get_categories_keyboard():
    async with AsyncSessionLocal() as db:
        categories = await db.execute(select(Category))
        categories = categories.scalars().all()

        if not categories:
            return None  # Если категорий нет

        builder = InlineKeyboardBuilder()
        for category in categories:
            builder.add(types.InlineKeyboardButton(
                text=category.name,
                callback_data=f"category_{category.category_id}"
            ))
        builder.adjust(2)  # Группируем кнопки по 2 в строке
        return builder.as_markup()

def get_orders_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📦 Просмотреть заказы", callback_data="view_orders"),
            InlineKeyboardButton(text="🔄 Изменить статус", callback_data="change_order_status")
        ],
        [
            InlineKeyboardButton(text="🔍 Поиск по ID", callback_data="search_order_by_id")
        ]
    ])
