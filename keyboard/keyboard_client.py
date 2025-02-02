from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder



contact = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отправить контакт', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Профиль ', request_contact=True), KeyboardButton(text='Корзина ', request_contact=True)],
    [KeyboardButton(text='Адрес магазина'), KeyboardButton(text='Заказать букет', request_contact=True)],
    [KeyboardButton(text='Сайт'), KeyboardButton(text='Youtube', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

main1 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Профиль ', request_contact=True)],
    [KeyboardButton(text='Корзина', request_contact=True)], 
    [KeyboardButton(text='Адрес магазина'), KeyboardButton(text='заказать букет', request_contact=True)],
    [KeyboardButton(text='Frwbb'), KeyboardButton(text='Сайт'), KeyboardButton(text='Youtube', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

profile = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заказать букет', request_contact=True), KeyboardButton(text='Корзина', request_contact=True)],  
 #   [KeyboardButton(text='История заказов')],
    [KeyboardButton(text='Меню', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

profile = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заказать букет', request_contact=True), KeyboardButton(text='Корзина', request_contact=True)],  
 #   [KeyboardButton(text='История заказов')],
    [KeyboardButton(text='Меню', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')


profile = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заказать букет', request_contact=True), KeyboardButton(text='Корзина', request_contact=True)],  
 #   [KeyboardButton(text='История заказов')],
    [KeyboardButton(text='Меню', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

profile = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заказать букет', request_contact=True), KeyboardButton(text='Корзина', request_contact=True)],  
 #   [KeyboardButton(text='История заказов')],
    [KeyboardButton(text='Меню', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')









contact = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отправить контакт', request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')