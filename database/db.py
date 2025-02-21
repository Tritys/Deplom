from sqlalchemy import Column, Integer, String, Float, ForeignKey, select, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import logging

DATABASE_URL = "sqlite+aiosqlite:///./flower_shop.db"

engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
AsyncSessionLocal  = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Модели
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True)
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
    
    available = Column(Boolean, default=True)

class Promotion(Base):
    __tablename__ = "promotions"
    promotion_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    description = Column(String)
    discount = Column(Float)
    
    start_date = Column(String)
    end_date = Column(String)

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
# Base.metadata.create_all(bind=engine)  # Создание таблиц заново
async def create_tables():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы созданы успешно!")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        
# Функции для работы с базой данных
async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

async def add_user(db: AsyncSession, id: int, user_id: int, first_name: str, username: str, phone: str = None):
    new_user = User(id=id, user_id=user_id, first_name=first_name, username=username, phone=phone)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.user_id == user_id))
    return result.scalars().first()


async def get_categories(db: AsyncSession):
    result = await db.execute(select(Category))
    return result.scalars().all()

async def get_bouquets_by_category(db: AsyncSession, category_id: int):
    result = await db.execute(select(Bouquet).filter(Bouquet.category_id == category_id))
    return result.scalars().all()

async def add_to_cart(db: AsyncSession, user_id: int, bouquet_id: int, quantity: int = 1):
    new_cart_item = Cart(user_id=user_id, bouquet_id=bouquet_id, quantity=quantity)
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    return new_cart_item

async def get_cart(db: AsyncSession, user_id):
    result = await db.execute(select(Cart).filter(Cart.user_id == user_id))
    return result.scalars().all()

async def clear_cart(db: AsyncSession, user_id):
    await db.execute(Cart.__table__.delete().where(Cart.user_id == user_id))
    await db.commit()

async def get_promotions(db: AsyncSession):
    result = await db.execute(select(Promotion))
    return result.scalars().all()

async def create_order(db: AsyncSession, user_id: int, total_price: float, delivery_type: str):
    new_order = Order(user_id=user_id, total_price=total_price, delivery_type=delivery_type)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

async def get_admin_orders(db: AsyncSession):
    result = await db.execute(select(Order).filter(Order.status == "pending"))
    return result.scalars().all()

async def update_order_status(db: AsyncSession, order_id, status):
    order = await db.execute(select(Order).filter(Order.order_id == order_id))
    order = order.scalars().first()
    if order:
        order.status = status
        db.commit()
        db.refresh(order)
    return order