from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
keyboard = InlineKeyboardBuilder()
    
# Меню
main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Профиль' ), KeyboardButton(text='Корзина' )],
    [KeyboardButton(text='Адрес магазина'), KeyboardButton(text='Заказать букет' )],
    [KeyboardButton(text='Сайт'), KeyboardButton(text='YouTube' )]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# Профиль
profile = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заказать букет' ), KeyboardButton(text='Корзина' )],  
    [KeyboardButton(text='Меню' ), KeyboardButton(text='Связь с администратором' )]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# 1.Заказать букет
category1 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Большие букеты' )],
    [KeyboardButton(text='День Рождение' ), KeyboardButton(text='8 марта' )],  
    [KeyboardButton(text='в корзине' ), KeyboardButton(text='в коробке' )],  
    [KeyboardButton(text='Мужские' ), KeyboardButton(text='Свадебные' )],  
    [KeyboardButton(text='Спасибо' ), KeyboardButton(text='Вместо извенений' )],  
    [KeyboardButton(text='День матери' ), KeyboardButton(text='Монобукеты' )],  
    [KeyboardButton(text='Траурные' ), KeyboardButton(text='Составные' )],  
    # [KeyboardButton(text='Цветы по штучно' )],
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
    [KeyboardButton(text='Траурные' ), KeyboardButton(text='Искусственные' )],  
    [KeyboardButton(text='Меню' ), KeyboardButton(text='назад' )]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# # 2.Заказать букет инлайн кнопки
# category = ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text='Заказать букет' ), KeyboardButton(text='Корзина' )],  
#     [KeyboardButton(text='Меню' ), KeyboardButton(text='Профиль' )]
# ], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

# Добавить букет в корзину 
def get_bouquet_kd(bouquet_id, category_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_{bouquet_id}_{category_id}"), InlineKeyboardButton(text="Далее ➡️", callback_data=f'next_{bouquet_id}_{category_id}')],
                [InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_{bouquet_id}")],
                [InlineKeyboardButton(text="Меню", callback_data='menu_'), InlineKeyboardButton(text="Список категорий", callback_data='category')],
        ]
    )
 
# Клавиатура для выбора доставки
delivery_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Доставка")],
        [KeyboardButton(text="Самовывоз")],
    ],
    resize_keyboard=True
)

# Клавиатура для выбора оплаты
payment_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Наличные")],
        [KeyboardButton(text="Карта")],
        [KeyboardButton(text="Перевод")],
    ], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')




# Корзина
def get_cart_keyboard(cart_items):
    builder = InlineKeyboardBuilder()
    
    for item in cart_items:
        # Кнопки для управления количеством
        builder.button(text=f"➖", callback_data=f"decrease_{item.bouquet_id}")
        builder.button(text=f"{item.quantity}", callback_data=f"quantity_{item.bouquet_id}")
        builder.button(text=f"➕", callback_data=f"increase_{item.bouquet_id}")
        # Кнопка для удаления букета
        builder.button(text=f"❌ Удалить", callback_data=f"remove_{item.bouquet_id}")
    
    # Кнопка для оформления заказа
    builder.button(text="Оформить заказ", callback_data="checkout")
    
    # Группируем кнопки: 3 кнопки на строку (управление количеством и удаление)
    builder.adjust(3, 1)  # 3 кнопки в первой строке, 1 кнопка на второй строке
    return builder.as_markup()
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

admin_contact = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Позвонить'), KeyboardButton(text='В чате')]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

contact_as = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Меню')]
], resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже.')

def You_tube():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='YouTube', url="https://www.youtube.com/")]])
    
def Website():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Сайт', url="https://www.youtube.com/")]])
    
    