from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram import types



main_admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Профиль' )],
    [KeyboardButton(text='Букеты'), KeyboardButton(text='Акции' )],
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')


def admin_bouquets():
    return InlineKeyboardMarkup( inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить букет", callback_data="add_bouquet"),
            InlineKeyboardButton(text="Удалить букет", callback_data="delete_bouquet"),
            InlineKeyboardButton(text="Изменить букет", callback_data="edit_bouquet"),
        ]])
    
def admin_promotions():
    return InlineKeyboardMarkup( inline_keyboard=[
        [
            InlineKeyboardButton("Добавить акцию", callback_data="add_promotion"),
            InlineKeyboardButton("Удалить акцию", callback_data="delete_promotion"),
            InlineKeyboardButton("Изменить акцию", callback_data="edit_promotion"),
        ]])