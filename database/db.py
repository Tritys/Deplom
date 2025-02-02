import sqlite3

def create_connection():
    return sqlite3.connect('data/flower_shop.db')

def init_db():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        username TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Bouquets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price REAL,
        category_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES Categories (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        bouquet_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES Users (id),
        FOREIGN KEY (bouquet_id) REFERENCES Bouquets (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Promotions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT
    )
    ''')

    conn.commit()
    conn.close()

def register_user(user_id, username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO Users (user_id, username) VALUES (?, ?)', (user_id, username))
    conn.commit()
    conn.close()

def get_categories():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Categories')
    categories = cursor.fetchall()
    conn.close()
    return categories

def get_bouquets_by_category(category_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Bouquets WHERE category_id = ?', (category_id,))
    bouquets = cursor.fetchall()
    conn.close()
    return bouquets

def add_to_cart(user_id, bouquet_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Cart (user_id, bouquet_id) VALUES (?, ?)', (user_id, bouquet_id))
    conn.commit()
    conn.close()

def get_cart(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT Bouquets.id, Bouquets.name, Bouquets.price 
    FROM Cart 
    JOIN Bouquets ON Cart.bouquet_id = Bouquets.id 
    WHERE Cart.user_id = ?
    ''', (user_id,))
    cart_items = cursor.fetchall()
    conn.close()
    return cart_items

def remove_from_cart(user_id, bouquet_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Cart WHERE user_id = ? AND bouquet_id = ?', (user_id, bouquet_id))
    conn.commit()
    conn.close()