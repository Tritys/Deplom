from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "sqlite:///./flower_shop.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
AsyncSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модели
class User(Base):
    __tablename__ = "users"
    first_name = Column(Integer, autoincrement=True)
    user_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    username = Column(String)
    phone = Column(String)

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

class Bouquet(Base):
    __tablename__ = "bouquets"
    bouquet_id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    name = Column(String)
    price = Column(Float)
    description = Column(String)
    image_url = Column(String)
    discount = Column(Float, default=0)

class Promotion(Base):
    __tablename__ = "promotions"
    promotion_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    description = Column(String)
    discount = Column(Float)

class Cart(Base):
    __tablename__ = "cart"
    cart_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    bouquet_id = Column(Integer, ForeignKey("bouquets.bouquet_id"))
    quantity = Column(Integer)

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    total_price = Column(Float)
    delivery_type = Column(String)
    status = Column(String, default="pending")

# Пересоздание таблиц
# Base.metadata.drop_all(bind=engine)  # Удаление всех таблиц
Base.metadata.create_all(bind=engine)  # Создание таблиц заново

# Функции для работы с базой данных
def get_db():
    db = AsyncSession()
    try:
        yield db
    finally:
        db.close()

def add_user(db: Session,id: int, user_id: int, first_name: str, username: str, phone: str = None):
    new_user = User(id=id, user_id=user_id, first_name=first_name, username=username, phone=phone)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


def get_user(db: Session, user_id):
    with AsyncSession() as db:
        return db.query(User).filter(User.user_id == user_id).first()

def get_categories(db: Session):
    return db.query(Category).all()

def get_bouquets_by_category(db: Session, category_id):
    return db.query(Bouquet).filter(Bouquet.category_id == category_id).all()

def add_to_cart(db: Session, user_id, bouquet_id, quantity=1):
    new_cart_item = Cart(user_id=user_id, bouquet_id=bouquet_id, quantity=quantity)
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    return new_cart_item

def get_cart(db: Session, user_id):
    return db.query(Cart).filter(Cart.user_id == user_id).all()

def clear_cart(db: Session, user_id):
    db.query(Cart).filter(Cart.user_id == user_id).delete()
    db.commit()

def get_promotions(db: Session):
    return db.query(Promotion).all()

def create_order(db: Session, user_id, total_price, delivery_type):
    new_order = Order(user_id=user_id, total_price=total_price, delivery_type=delivery_type)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

def get_admin_orders(db: Session):
    return db.query(Order).filter(Order.status == "pending").all()

def update_order_status(db: Session, order_id, status):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if order:
        order.status = status
        db.commit()
        db.refresh(order)
    return order