from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
keyboard = InlineKeyboardBuilder()
    
# Меню
main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Профиль' ), KeyboardButton(text='Корзина' )],
    [KeyboardButton(text='Адрес магазина'), KeyboardButton(text='Заказать букет' )],
    [KeyboardButton(text='Сайт'), KeyboardButton(text='Youtube' )]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# Профиль
profile = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заказать букет' ), KeyboardButton(text='Корзина' )],  
    [KeyboardButton(text='Меню' ), KeyboardButton(text='Связь с администратороменю' )]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# 1.Заказать букет
category1 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Большие букеты' )],
    [KeyboardButton(text='День Рождения' ), KeyboardButton(text='8 марта' )],  
    [KeyboardButton(text='в корзине' ), KeyboardButton(text='в коробке' )],  
    [KeyboardButton(text='Мужские' ), KeyboardButton(text='Свадебные' )],  
    [KeyboardButton(text='Спасибо' ), KeyboardButton(text='Извини' )],  
    [KeyboardButton(text='День матери' ), KeyboardButton(text='Монобукеты' )],  
    [KeyboardButton(text='Траурные' ), KeyboardButton(text='Искусственные' )],  
    [KeyboardButton(text='Цветы по штучно' )],
    [KeyboardButton(text='Меню' ), KeyboardButton(text='Корзина' )]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# 2.Заказать букет инлайн кнопки
category = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заказать букет' ), KeyboardButton(text='Корзина' )],  
    [KeyboardButton(text='Меню' ), KeyboardButton(text='Профиль' )]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# Большие букеты
category2 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Розы' ), KeyboardButton(text='Тюльпаны' )],  
    [KeyboardButton(text='Хризантемы' ), KeyboardButton(text='Ромашки' )],  
    [KeyboardButton(text='Лилии' ), KeyboardButton(text='Гортензии' )],  
    [KeyboardButton(text='Ирисы' ), KeyboardButton(text='Нарциссы' )],  
    [KeyboardButton(text='Пионы' ), KeyboardButton(text='Эустома' )],  
    [KeyboardButton(text='Траурные' ), KeyboardButton(text='Ирисы' )],  
    [KeyboardButton(text='Меню' ), KeyboardButton(text='назад' )]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# # 2.Заказать букет инлайн кнопки
# category = ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text='Заказать букет' ), KeyboardButton(text='Корзина' )],  
#     [KeyboardButton(text='Меню' ), KeyboardButton(text='Профиль' )]
# ], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# Добавить букет в корзину 
def get_bouquet_kd(bouquet_id, category_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_{bouquet_id}_{category_id}"), InlineKeyboardButton(text="Далее ➡️", callback_data=f'next_{bouquet_id}_{category_id}'))
    keyboard.add(InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_{bouquet_id}"))
    keyboard.add(InlineKeyboardButton(text="Меню", callback_data='menu_'), InlineKeyboardButton(text="Список категорий", callback_data='category_'))
    return keyboard
    
    




# Корзина
cart = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заказать букет' ), KeyboardButton(text='Корзина' )],  
    [KeyboardButton(text='Меню' )]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# Адрес магазина
shop_address = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='О магазине ℹ️' ), KeyboardButton(text='Заказать букет' )],  
    [KeyboardButton(text='Меню' )]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# О магазине
shop = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Меню'), KeyboardButton(text='Профиль')]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

contact = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отправить контакт' , request_contact=True)]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Меню')]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')



def You_tube():
    keyboard.add(InlineKeyboardButton(text='YouTube', url="https://www.youtube.com/"))
    
def Website():
    keyboard.add(InlineKeyboardButton(text='Сайт', url="https://www.youtube.com/"))