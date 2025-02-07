from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
keyboard = InlineKeyboardBuilder()
    
# Меню
main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Профиль ', request_contact=True), KeyboardButton(text='Корзина ', request_contact=True)],
    [KeyboardButton(text='Адрес магазина'), KeyboardButton(text='Заказать букет', request_contact=True)],
    [KeyboardButton(text='Сайт'), KeyboardButton(text='Youtube', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# Профиль
profile = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заказать букет', request_contact=True), KeyboardButton(text='Корзина', request_contact=True)],  
    [KeyboardButton(text='Меню', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# 1.Категории используется
category = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заказать букет', request_contact=True), KeyboardButton(text='Корзина', request_contact=True)],  
    [KeyboardButton(text='Меню', request_contact=True), KeyboardButton(text='Профиль', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# 2.Категории
category = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заказать букет', request_contact=True), KeyboardButton(text='Корзина', request_contact=True)],  
    [KeyboardButton(text='Меню', request_contact=True), KeyboardButton(text='Профиль', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# Корзина
cart = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заказать букет', request_contact=True), KeyboardButton(text='Корзина', request_contact=True)],  
    [KeyboardButton(text='Меню', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# Адрес магазина
profile = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='О магазине ℹ️', request_contact=True), KeyboardButton(text='Заказать букет', request_contact=True)],  
    [KeyboardButton(text='Меню', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')






contact = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отправить контакт', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')



def You_tube():
    keyboard.add(InlineKeyboardButton(text='YouTube', url="https://www.youtube.com/"))
    
def Website():
    keyboard.add(InlineKeyboardButton(text='Сайт', url="https://www.youtube.com/"))