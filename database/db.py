import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_tables():
    conn = sqlite3.connect('flower_shop.db')
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            phone_number TEXT
        )
    ''')

    # Таблица категорий
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    ''')

    # Таблица букетов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bouquets (
            bouquet_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            name TEXT,
            price REAL,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (category_id)
        )
    ''')

    # Таблица акций
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promotions (
            promotion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            discount REAL
        )
    ''')

    # Таблица корзины
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            bouquet_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (bouquet_id) REFERENCES bouquets (bouquet_id)
        )
    ''')

    # Таблица заказов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            total_price REAL,
            delivery_type TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    conn.commit()
    conn.close()

def add_user(user_id, phone_number):
    conn = sqlite3.connect('flower_shop.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (user_id, phone_number) VALUES (?, ?)', (user_id, phone_number))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('flower_shop.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_categories():
    conn = sqlite3.connect('flower_shop.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categories')
    categories = cursor.fetchall()
    conn.close()
    return categories

def get_bouquets_by_category(category_id):
    conn = sqlite3.connect('flower_shop.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bouquets WHERE category_id = ?', (category_id,))
    bouquets = cursor.fetchall()
    conn.close()
    return bouquets

def add_to_cart(user_id, bouquet_id, quantity=1):
    conn = sqlite3.connect('flower_shop.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO cart (user_id, bouquet_id, quantity) VALUES (?, ?, ?)', (user_id, bouquet_id, quantity))
    conn.commit()
    conn.close()

def get_cart(user_id):
    conn = sqlite3.connect('flower_shop.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT bouquets.name, bouquets.price, cart.quantity 
        FROM cart 
        JOIN bouquets ON cart.bouquet_id = bouquets.bouquet_id 
        WHERE cart.user_id = ?
    ''', (user_id,))
    cart_items = cursor.fetchall()
    conn.close()
    return cart_items

def clear_cart(user_id):
    conn = sqlite3.connect('flower_shop.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_promotions():
    conn = sqlite3.connect('flower_shop.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM promotions')
    promotions = cursor.fetchall()
    conn.close()
    return promotions

def create_order(user_id, total_price, delivery_type):
    conn = sqlite3.connect('flower_shop.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (user_id, total_price, delivery_type) VALUES (?, ?, ?)', (user_id, total_price, delivery_type))
    conn.commit()
    conn.close()

def get_admin_orders():
    conn = sqlite3.connect('flower_shop.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE status = "pending"')
    orders = cursor.fetchall()
    conn.close()
    return orders

def update_order_status(order_id, status):
    conn = sqlite3.connect('flower_shop.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE orders SET status = ? WHERE order_id = ?', (status, order_id))
    conn.commit()
    conn.close()
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()