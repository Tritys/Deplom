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

# 1.Заказать букет
category = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Большие букеты', request_contact=True)],
    [KeyboardButton(text='День Рождения', request_contact=True), KeyboardButton(text='8 марта', request_contact=True)],  
    [KeyboardButton(text='в корзине', request_contact=True), KeyboardButton(text='в коробке', request_contact=True)],  
    [KeyboardButton(text='Мужские', request_contact=True), KeyboardButton(text='Свадебные', request_contact=True)],  
    [KeyboardButton(text='Спасибо', request_contact=True), KeyboardButton(text='Извини', request_contact=True)],  
    [KeyboardButton(text='День матери', request_contact=True), KeyboardButton(text='Монобукеты', request_contact=True)],  
    [KeyboardButton(text='Траурные', request_contact=True), KeyboardButton(text='Искусственные', request_contact=True)],  
    [KeyboardButton(text='Цветы по штучно', request_contact=True)],
    [KeyboardButton(text='Меню', request_contact=True), KeyboardButton(text='Корзина', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# 2.Заказать букет инлайн кнопки
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
shop_address = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='О магазине ℹ️', request_contact=True), KeyboardButton(text='Заказать букет', request_contact=True)],  
    [KeyboardButton(text='Меню', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# О магазине
shop = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Меню', request_contact=True), KeyboardButton(text='О магазине ℹ️', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

contact = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отправить контакт', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')



def You_tube():
    keyboard.add(InlineKeyboardButton(text='YouTube', url="https://www.youtube.com/"))
    
def Website():
    keyboard.add(InlineKeyboardButton(text='Сайт', url="https://www.youtube.com/"))