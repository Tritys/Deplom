from sqlalchemy import Column, Integer, String, Float, ForeignKey, select, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import logging
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import relationship
from sqlalchemy.orm import joinedload

DATABASE_URL = "sqlite+aiosqlite:///./flower_shop.db"

engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
AsyncSessionLocal  = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Модели
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    username = Column(String)
    phone = Column(String)

class Category(Base):
    __tablename__ = "categorys"
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)

class Bouquet(AsyncAttrs, Base):
    __tablename__ = "bouquets"
    bouquet_id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categorys.category_id", ondelete="CASCADE"), index=True)
    name = Column(String, index=True)
    price = Column(Float)
    description = Column(String)
    image_url = Column(String)
    discount = Column(Float, default=0)
    available = Column(Boolean, default=True)
    
    # Определяем связь с моделью Cart
    carts = relationship("Cart", back_populates="bouquet", cascade="all, delete-orphan")
    

class Promotion(Base):
    __tablename__ = "promotions"
    promotion_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    description = Column(String)
    discount = Column(Float)
    
    start_date = Column(String)
    end_date = Column(String)

class Cart(Base):
    __tablename__ = "carts"
    cart_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    bouquet_id = Column(Integer, ForeignKey("bouquets.bouquet_id", ondelete="CASCADE"), index=True)
    quantity = Column(Integer)
    
    # Определяем связь с моделью Bouquet
    bouquet = relationship("Bouquet", back_populates="carts")

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    total_price = Column(Float)
    delivery_type = Column(String)
    payment_method = Column(String)  # Новый столбец
    status = Column(String, default="pending", index=True)
    created_at = Column(DateTime, default=func.now())  # Дата создания заказа

    # Связь с таблицей order_items (если нужно хранить товары в заказе)
    items = relationship("OrderItem", back_populates="order")
    
class OrderItem(Base):
    __tablename__ = "order_items"
    order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), index=True)
    bouquet_id = Column(Integer, ForeignKey("bouquets.bouquet_id", ondelete="CASCADE"), index=True)
    quantity = Column(Integer)
    price = Column(Float)  # Цена на момент заказа

    # Связи
    order = relationship("Order", back_populates="items")
    bouquet = relationship("Bouquet")

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
    try:
        new_user = User(user_id=user_id, first_name=first_name, username=username, phone=phone)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка при добавлении пользователя: {e}")
        raise


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
    try:
        new_cart_item = Cart(user_id=user_id, bouquet_id=bouquet_id, quantity=quantity)
        db.add(new_cart_item)
        await db.commit()
        await db.refresh(new_cart_item)
        logger.info(f"Добавлен элемент в корзину: {new_cart_item}")
        return new_cart_item
    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка при добавлении в корзину: {e}")
        raise

async def get_cart(db: AsyncSession, user_id):
    logger.info(f"Запрос корзины для пользователя {user_id}")
    result = await db.execute(select(Cart).filter(Cart.user_id == user_id))
    items = result.scalars().all()
    logger.info(f"Найдено элементов в корзине: {len(items)}")
    return items

async def clear_cart(db: AsyncSession, user_id):
    result = await db.execute(
        select(Cart, Bouquet)
        .join(Bouquet, Cart.bouquet_id == Bouquet.bouquet_id)
        .filter(Cart.user_id == user_id)
    )
    return result.all()
async def get_promotions(db: AsyncSession):
    result = await db.execute(select(Promotion))
    return result.scalars().all()

async def create_order(db: AsyncSession, user_id: int, total_price: float, delivery_type: str):
    new_order = Order(user_id=user_id, total_price=total_price, delivery_type=delivery_type)
    db.add(new_order)
    await  db.commit()
    await  db.refresh(new_order)
    return new_order

# Функция для получения заказов с загруженными товарами
async def get_admin_orders(db: AsyncSession):
    result = await db.execute(
        select(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.bouquet))  # Загружаем связанные данные
    )
    return result.scalars().all()

async def update_order_status(db: AsyncSession, order_id: int, status: str):
    order = await db.execute(select(Order).where(Order.order_id == order_id))
    order = order.scalars().first()
    if order:
        order.status = status
        await db.commit()
        await db.refresh(order)
        return order
    return None




# Заполнение таблицы bouquets
bouquets = [
    (1111, 'Яркий праздник', 70.00, 'Яркие цветы для яркого дня рождения', 'http://example.com/birthday1.jpg', 0.0, 1),
    (1111, 'Розовый восторг', 85.00, 'Нежные розы для особенного дня', 'http://example.com/birthday2.jpg', 5.0, 1),
    (1111, 'Солнечный день', 60.00, 'Желтые тюльпаны для радости', 'http://example.com/birthday3.jpg', 0.0, 1),
    (1111, 'Летний бриз', 75.00, 'Свежие лилии и ромашки', 'http://example.com/birthday4.jpg', 10.0, 1),
    (1111, 'Классика жанра', 90.00, 'Красные розы в классическом стиле', 'http://example.com/birthday5.jpg', 0.0, 1),
    (1111, 'Нежность', 65.00, 'Белые пионы и эустомы', 'http://example.com/birthday6.jpg', 0.0, 1),
    (1111, 'Элегантность', 80.00, 'Гортензии и розы в пастельных тонах', 'http://example.com/birthday7.jpg', 0.0, 1),
    (1111, 'Феерия красок', 95.00, 'Разноцветные ирисы и тюльпаны', 'http://example.com/birthday8.jpg', 0.0, 1),
    (1111, 'Весенний букет', 70.00, 'Нарциссы и ромашки', 'http://example.com/birthday9.jpg', 0.0, 1),
    (1111, 'Королевский подарок', 100.00, 'Роскошные розы и лилии', 'http://example.com/birthday10.jpg', 0.0, 1),

(1112, 'Весеннее настроение', 55.00, 'Тюльпаны и нарциссы', 'http://example.com/march8_1.jpg', 0.0, 1),
(1112, 'Нежность весны', 65.00, 'Розовые розы и пионы', 'http://example.com/march8_2.jpg', 0.0, 1),
(1112, 'Солнечный букет', 50.00, 'Желтые тюльпаны и ромашки', 'http://example.com/march8_3.jpg', 0.0, 1),
(1112, 'Лавандовый сон', 70.00, 'Лавандовые розы и эустомы', 'http://example.com/march8_4.jpg', 0.0, 1),
(1112, 'Весенний вальс', 60.00, 'Белые лилии и розы', 'http://example.com/march8_5.jpg', 0.0, 1),
(1112, 'Цветочная фантазия', 75.00, 'Разноцветные ирисы и тюльпаны', 'http://example.com/march8_6.jpg', 0.0, 1),
(1112, 'Нежный букет', 65.00, 'Розовые пионы и гортензии', 'http://example.com/march8_7.jpg', 0.0, 1),
(1112, 'Свежесть весны', 55.00, 'Белые ромашки и нарциссы', 'http://example.com/march8_8.jpg', 0.0, 1),
(1112, 'Розовый закат', 80.00, 'Розовые розы и лилии', 'http://example.com/march8_9.jpg', 0.0, 1),
(1112, 'Весенний подарок', 70.00, 'Тюльпаны и розы', 'http://example.com/march8_10.jpg', 0.0, 1),


(1113, 'Деревенский шарм', 90.00, 'Цветы в плетеной корзине', 'http://example.com/basket1.jpg', 0.0, 1),
(1113, 'Летний сад', 85.00, 'Смесь полевых цветов в корзине', 'http://example.com/basket2.jpg', 0.0, 1),
(1113, 'Романтический вечер', 95.00, 'Розы и лилии в корзине', 'http://example.com/basket3.jpg', 0.0, 1),
(1113, 'Свежесть утра', 80.00, 'Ромашки и тюльпаны в корзине', 'http://example.com/basket4.jpg', 0.0, 1),
(1113, 'Элегантность', 100.00, 'Гортензии и розы в корзине', 'http://example.com/basket5.jpg', 0.0, 1),
(1113, 'Весенний букет', 75.00, 'Тюльпаны и нарциссы в корзине', 'http://example.com/basket6.jpg', 0.0, 1),
(1113, 'Нежность', 85.00, 'Пионы и эустомы в корзине', 'http://example.com/basket7.jpg', 0.0, 1),
(1113, 'Цветочный рай', 90.00, 'Разноцветные ирисы в корзине', 'http://example.com/basket8.jpg', 0.0, 1),
(1113, 'Классика', 95.00, 'Красные розы в корзине', 'http://example.com/basket9.jpg', 0.0, 1),
(1113, 'Солнечный день', 80.00, 'Желтые тюльпаны в корзине', 'http://example.com/basket10.jpg', 0.0, 1),

(1114, 'Классическая коробка', 80.00, 'Красные розы в элегантной коробке', 'http://example.com/box1.jpg', 0.0, 1),
(1114, 'Розовая нежность', 90.00, 'Розовые розы в коробке', 'http://example.com/box2.jpg', 5.0, 1),
(1114, 'Белая элегантность', 85.00, 'Белые розы в коробке', 'http://example.com/box3.jpg', 0.0, 1),
(1114, 'Яркие эмоции', 75.00, 'Разноцветные розы в коробке', 'http://example.com/box4.jpg', 0.0, 1),
(1114, 'Летний день', 70.00, 'Тюльпаны в коробке', 'http://example.com/box5.jpg', 0.0, 1),
(1114, 'Нежность пионов', 95.00, 'Пионы в коробке', 'http://example.com/box6.jpg', 0.0, 1),
(1114, 'Элегантность лилий', 100.00, 'Лилии в коробке', 'http://example.com/box7.jpg', 0.0, 1),
(1114, 'Свежесть гортензий', 85.00, 'Гортензии в коробке', 'http://example.com/box8.jpg', 0.0, 1),
(1114, 'Романтика', 90.00, 'Розы и пионы в коробке', 'http://example.com/box9.jpg', 0.0, 1),
(1114, 'Королевский подарок', 120.00, 'Роскошные розы в коробке', 'http://example.com/box10.jpg', 0.0, 1),

(1115, 'Мужской стиль', 70.00, 'Букет в темных тонах', 'http://example.com/men1.jpg', 0.0, 1),
(1115, 'Сила и элегантность', 80.00, 'Красные розы и зелень', 'http://example.com/men2.jpg', 0.0, 1),
(1115, 'Классика', 75.00, 'Белые розы и эвкалипт', 'http://example.com/men3.jpg', 0.0, 1),
(1115, 'Сдержанность', 85.00, 'Темные розы и гортензии', 'http://example.com/men4.jpg', 0.0, 1),
(1115, 'Мужской шарм', 90.00, 'Розы и суккуленты', 'http://example.com/men5.jpg', 0.0, 1),
(1115, 'Синий акцент', 65.00, 'Синие ирисы и зелень', 'http://example.com/men6.jpg', 0.0, 1),
(1115, 'Темная элегантность', 95.00, 'Бордовые розы и эвкалипт', 'http://example.com/men7.jpg', 0.0, 1),
(1115, 'Строгость', 70.00, 'Черные розы и зелень', 'http://example.com/men8.jpg', 0.0, 1),
(1115, 'Мужской букет', 80.00, 'Розы и хризантемы', 'http://example.com/men9.jpg', 0.0, 1),
(1115, 'Классический стиль', 85.00, 'Белые и красные розы', 'http://example.com/men10.jpg', 0.0, 1),

(1116, 'Свадебная нежность', 120.00, 'Белые розы и пионы', 'http://example.com/wedding1.jpg', 0.0, 1),
(1116, 'Элегантность невесты', 130.00, 'Белые лилии и розы', 'http://example.com/wedding2.jpg', 0.0, 1),
(1116, 'Романтический букет', 110.00, 'Розовые розы и эустомы', 'http://example.com/wedding3.jpg', 0.0, 1),
(1116, 'Классический свадебный', 100.00, 'Белые розы и зелень', 'http://example.com/wedding4.jpg', 0.0, 1),
(1116, 'Свадебный вальс', 115.00, 'Белые пионы и гортензии', 'http://example.com/wedding5.jpg', 0.0, 1),
(1116, 'Нежность', 125.00, 'Белые розы и эвкалипт', 'http://example.com/wedding6.jpg', 0.0, 1),
(1116, 'Свадебная феерия', 140.00, 'Белые и розовые розы', 'http://example.com/wedding7.jpg', 0.0, 1),
(1116, 'Свадебный букет', 105.00, 'Белые тюльпаны и розы', 'http://example.com/wedding8.jpg', 0.0, 1),
(1116, 'Свадебная элегантность', 135.00, 'Белые лилии и пионы', 'http://example.com/wedding9.jpg', 0.0, 1),
(1116, 'Свадебный подарок', 150.00, 'Белые розы и орхидеи', 'http://example.com/wedding10.jpg', 0.0, 1),

(1117, 'Благодарность', 60.00, 'Яркие цветы для выражения благодарности', 'http://example.com/thanks1.jpg', 0.0, 1),
(1117, 'Спасибо за все', 70.00, 'Нежные розы и ромашки', 'http://example.com/thanks2.jpg', 0.0, 1),
(1117, 'Искренняя благодарность', 65.00, 'Букет из тюльпанов и хризантем', 'http://example.com/thanks3.jpg', 0.0, 1),
(1117, 'Спасибо за помощь', 75.00, 'Яркие ирисы и розы', 'http://example.com/thanks4.jpg', 0.0, 1),
(1117, 'Благодарность и уважение', 80.00, 'Элегантные лилии и розы', 'http://example.com/thanks5.jpg', 0.0, 1),
(1117, 'Спасибо за заботу', 70.00, 'Нежные пионы и эустомы', 'http://example.com/thanks6.jpg', 0.0, 1),
(1117, 'Спасибо за поддержку', 85.00, 'Гортензии и розы', 'http://example.com/thanks7.jpg', 0.0, 1),
(1117, 'Спасибо за дружбу', 90.00, 'Разноцветные тюльпаны и нарциссы', 'http://example.com/thanks8.jpg', 0.0, 1),
(1117, 'Спасибо за тепло', 65.00, 'Ромашки и хризантемы', 'http://example.com/thanks9.jpg', 0.0, 1),
(1117, 'Спасибо за вдохновение', 100.00, 'Розы и лилии', 'http://example.com/thanks10.jpg', 0.0, 1),

(1118, 'Искренние извинения', 70.00, 'Нежные розы для выражения сожаления', 'http://example.com/sorry1.jpg', 0.0, 1),
(1118, 'Прости меня', 65.00, 'Белые лилии и розы', 'http://example.com/sorry2.jpg', 0.0, 1),
(1118, 'Извини за все', 75.00, 'Букет из тюльпанов и хризантем', 'http://example.com/sorry3.jpg', 0.0, 1),
(1118, 'Сожалею', 80.00, 'Нежные пионы и эустомы', 'http://example.com/sorry4.jpg', 0.0, 1),
(1118, 'Прости, пожалуйста', 85.00, 'Гортензии и розы', 'http://example.com/sorry5.jpg', 0.0, 1),
(1118, 'Искреннее сожаление', 90.00, 'Разноцветные тюльпаны и нарциссы', 'http://example.com/sorry6.jpg', 0.0, 1),
(1118, 'Прости за ошибку', 65.00, 'Ромашки и хризантемы', 'http://example.com/sorry7.jpg', 0.0, 1),
(1118, 'Извини за опоздание', 100.00, 'Розы и лилии', 'http://example.com/sorry8.jpg', 0.0, 1),
(1118, 'Сожалею от всего сердца', 70.00, 'Белые розы и эвкалипт', 'http://example.com/sorry9.jpg', 0.0, 1),
(1118, 'Прости за недоразумение', 75.00, 'Нежные пионы и розы', 'http://example.com/sorry10.jpg', 0.0, 1),

(1119, 'Любовь к маме', 80.00, 'Нежные розы для мамы', 'http://example.com/mother1.jpg', 0.0, 1),
(1119, 'Спасибо, мама', 85.00, 'Букет из пионов и роз', 'http://example.com/mother2.jpg', 0.0, 1),
(1119, 'Мамина радость', 90.00, 'Яркие тюльпаны и хризантемы', 'http://example.com/mother3.jpg', 0.0, 1),
(1119, 'Нежность для мамы', 95.00, 'Белые лилии и розы', 'http://example.com/mother4.jpg', 0.0, 1),
(1119, 'Мамино счастье', 100.00, 'Розовые пионы и эустомы', 'http://example.com/mother5.jpg', 0.0, 1),
(1119, 'Любимой маме', 105.00, 'Гортензии и розы', 'http://example.com/mother6.jpg', 0.0, 1),
(1119, 'Мамина гордость', 110.00, 'Разноцветные тюльпаны и нарциссы', 'http://example.com/mother7.jpg', 0.0, 1),
(1119, 'Мамина улыбка', 115.00, 'Ромашки и хризантемы', 'http://example.com/mother8.jpg', 0.0, 1),
(1119, 'Мамина любовь', 120.00, 'Розы и лилии', 'http://example.com/mother9.jpg', 0.0, 1),
(1119, 'Мамино тепло', 125.00, 'Белые розы и эвкалипт', 'http://example.com/mother10.jpg', 0.0, 1),

(1120, 'Красные розы', 50.00, 'Букет из красных роз', 'http://example.com/mono1.jpg', 0.0, 1),
(1120, 'Белые розы', 55.00, 'Букет из белых роз', 'http://example.com/mono2.jpg', 0.0, 1),
(1120, 'Розовые розы', 60.00, 'Букет из розовых роз', 'http://example.com/mono3.jpg', 0.0, 1),
(1120, 'Желтые тюльпаны', 45.00, 'Букет из желтых тюльпанов', 'http://example.com/mono4.jpg', 0.0, 1),
(1120, 'Белые лилии', 70.00, 'Букет из белых лилий', 'http://example.com/mono5.jpg', 0.0, 1),
(1120, 'Розовые пионы', 65.00, 'Букет из розовых пионов', 'http://example.com/mono6.jpg', 0.0, 1),
(1120, 'Синие ирисы', 50.00, 'Букет из синих ирисов', 'http://example.com/mono7.jpg', 0.0, 1),
(1120, 'Белые хризантемы', 55.00, 'Букет из белых хризантем', 'http://example.com/mono8.jpg', 0.0, 1),
(1120, 'Красные тюльпаны', 60.00, 'Букет из красных тюльпанов', 'http://example.com/mono9.jpg', 0.0, 1),
(1120, 'Белые эустомы', 70.00, 'Букет из белых эустом', 'http://example.com/mono10.jpg', 0.0, 1),

(1121, 'Траурный букет из роз', 80.00, 'Букет из темных роз', 'http://example.com/mourning1.jpg', 0.0, 1),
(1121, 'Траурный букет из лилий', 85.00, 'Букет из белых лилий', 'http://example.com/mourning2.jpg', 0.0, 1),
(1121, 'Траурный букет из хризантем', 75.00, 'Букет из белых хризантем', 'http://example.com/mourning3.jpg', 0.0, 1),
(1121, 'Траурный букет из гвоздик', 70.00, 'Букет из красных гвоздик', 'http://example.com/mourning4.jpg', 0.0, 1),
(1121, 'Траурный букет из роз и лилий', 90.00, 'Букет из роз и лилий', 'http://example.com/mourning5.jpg', 0.0, 1),
(1121, 'Траурный букет из роз и хризантем', 95.00, 'Букет из роз и хризантем', 'http://example.com/mourning6.jpg', 0.0, 1),
(1121, 'Траурный букет из роз и гвоздик', 100.00, 'Букет из роз и гвоздик', 'http://example.com/mourning7.jpg', 0.0, 1),
(1121, 'Траурный букет из лилий и хризантем', 85.00, 'Букет из лилий и хризантем', 'http://example.com/mourning8.jpg', 0.0, 1),
(1121, 'Траурный букет из гвоздик и хризантем', 80.00, 'Букет из гвоздик и хризантем', 'http://example.com/mourning9.jpg', 0.0, 1),
(1121, 'Траурный букет из роз, лилий и хризантем', 120.00, 'Букет из роз, лилий и хризантем', 'http://example.com/mourning10.jpg', 0.0, 1),

(1122, 'Яркий микс', 90.00, 'Букет из роз, тюльпанов и хризантем', 'http://example.com/mix1.jpg', 0.0, 1),
(1122, 'Нежный микс', 85.00, 'Букет из роз, лилий и эустом', 'http://example.com/mix2.jpg', 0.0, 1),
(1122, 'Свежий микс', 80.00, 'Букет из тюльпанов, ромашек и хризантем', 'http://example.com/mix3.jpg', 0.0, 1),
(1122, 'Элегантный микс', 95.00, 'Букет из роз, пионов и гортензий', 'http://example.com/mix4.jpg', 0.0, 1),
(1122, 'Летний микс', 75.00, 'Букет из роз, нарциссов и ирисов', 'http://example.com/mix5.jpg', 0.0, 1),
(1122, 'Романтический микс', 100.00, 'Букет из роз, лилий и тюльпанов', 'http://example.com/mix6.jpg', 0.0, 1),
(1122, 'Весенний микс', 85.00, 'Букет из тюльпанов, ромашек и нарциссов', 'http://example.com/mix7.jpg', 0.0, 1),
(1122, 'Осенний микс', 90.00, 'Букет из роз, хризантем и гортензий', 'http://example.com/mix8.jpg', 0.0, 1),
(1122, 'Зимний микс', 95.00, 'Букет из роз, лилий и эустом', 'http://example.com/mix9.jpg', 0.0, 1),
(1122, 'Фантазийный микс', 110.00, 'Букет из роз, пионов, лилий и тюльпанов', 'http://example.com/mix10.jpg', 0.0, 1),

(2111, 'Красные розы', 50.00, 'Букет из красных роз', 'http://example.com/roses1.jpg', 0.0, 1),
(2111, 'Белые розы', 55.00, 'Букет из белых роз', 'http://example.com/roses2.jpg', 0.0, 1),
(2111, 'Розовые розы', 60.00, 'Букет из розовых роз', 'http://example.com/roses3.jpg', 0.0, 1),
(2111, 'Желтые розы', 65.00, 'Букет из желтых роз', 'http://example.com/roses4.jpg', 0.0, 1),
(2111, 'Оранжевые розы', 70.00, 'Букет из оранжевых роз', 'http://example.com/roses5.jpg', 0.0, 1),
(2111, 'Синие розы', 75.00, 'Букет из синих роз', 'http://example.com/roses6.jpg', 0.0, 1),
(2111, 'Фиолетовые розы', 80.00, 'Букет из фиолетовых роз', 'http://example.com/roses7.jpg', 0.0, 1),
(2111, 'Черные розы', 85.00, 'Букет из черных роз', 'http://example.com/roses8.jpg', 0.0, 1),
(2111, 'Многоцветные розы', 90.00, 'Букет из многоцветных роз', 'http://example.com/roses9.jpg', 0.0, 1),
(2111, 'Розы в коробке', 100.00, 'Букет из роз в коробке', 'http://example.com/roses10.jpg', 0.0, 1),

(2112, 'Красные тюльпаны', 40.00, 'Букет из красных тюльпанов', 'http://example.com/tulips1.jpg', 0.0, 1),
(2112, 'Желтые тюльпаны', 45.00, 'Букет из желтых тюльпанов', 'http://example.com/tulips2.jpg', 0.0, 1),
(2112, 'Розовые тюльпаны', 50.00, 'Букет из розовых тюльпанов', 'http://example.com/tulips3.jpg', 0.0, 1),
(2112, 'Белые тюльпаны', 55.00, 'Букет из белых тюльпанов', 'http://example.com/tulips4.jpg', 0.0, 1),
(2112, 'Фиолетовые тюльпаны', 60.00, 'Букет из фиолетовых тюльпанов', 'http://example.com/tulips5.jpg', 0.0, 1),
(2112, 'Оранжевые тюльпаны', 65.00, 'Букет из оранжевых тюльпанов', 'http://example.com/tulips6.jpg', 0.0, 1),
(2112, 'Многоцветные тюльпаны', 70.00, 'Букет из многоцветных тюльпанов', 'http://example.com/tulips7.jpg', 0.0, 1),
(2112, 'Тюльпаны в коробке', 75.00, 'Букет из тюльпанов в коробке', 'http://example.com/tulips8.jpg', 0.0, 1),
(2112, 'Тюльпаны с зеленью', 80.00, 'Букет из тюльпанов с зеленью', 'http://example.com/tulips9.jpg', 0.0, 1),
(2112, 'Тюльпаны и розы', 85.00, 'Букет из тюльпанов и роз', 'http://example.com/tulips10.jpg', 0.0, 1),

(2113, 'Белые хризантемы', 50.00, 'Букет из белых хризантем', 'http://example.com/chrys1.jpg', 0.0, 1),
(2113, 'Желтые хризантемы', 55.00, 'Букет из желтых хризантем', 'http://example.com/chrys2.jpg', 0.0, 1),
(2113, 'Розовые хризантемы', 60.00, 'Букет из розовых хризантем', 'http://example.com/chrys3.jpg', 0.0, 1),
(2113, 'Красные хризантемы', 65.00, 'Букет из красных хризантем', 'http://example.com/chrys4.jpg', 0.0, 1),
(2113, 'Фиолетовые хризантемы', 70.00, 'Букет из фиолетовых хризантем', 'http://example.com/chrys5.jpg', 0.0, 1),
(2113, 'Оранжевые хризантемы', 75.00, 'Букет из оранжевых хризантем', 'http://example.com/chrys6.jpg', 0.0, 1),
(2113, 'Многоцветные хризантемы', 80.00, 'Букет из многоцветных хризантем', 'http://example.com/chrys7.jpg', 0.0, 1),
(2113, 'Хризантемы в коробке', 85.00, 'Букет из хризантем в коробке', 'http://example.com/chrys8.jpg', 0.0, 1),
(2113, 'Хризантемы с зеленью', 90.00, 'Букет из хризантем с зеленью', 'http://example.com/chrys9.jpg', 0.0, 1),
(2113, 'Хризантемы и розы', 95.00, 'Букет из хризантем и роз', 'http://example.com/chrys10.jpg', 0.0, 1),

(2114, 'Белые ромашки', 30.00, 'Букет из белых ромашек', 'http://example.com/daisy1.jpg', 0.0, 1),
(2114, 'Желтые ромашки', 35.00, 'Букет из желтых ромашек', 'http://example.com/daisy2.jpg', 0.0, 1),
(2114, 'Розовые ромашки', 40.00, 'Букет из розовых ромашек', 'http://example.com/daisy3.jpg', 0.0, 1),
(2114, 'Красные ромашки', 45.00, 'Букет из красных ромашек', 'http://example.com/daisy4.jpg', 0.0, 1),
(2114, 'Фиолетовые ромашки', 50.00, 'Букет из фиолетовых ромашек', 'http://example.com/daisy5.jpg', 0.0, 1),
(2114, 'Оранжевые ромашки', 55.00, 'Букет из оранжевых ромашек', 'http://example.com/daisy6.jpg', 0.0, 1),
(2114, 'Многоцветные ромашки', 60.00, 'Букет из многоцветных ромашек', 'http://example.com/daisy7.jpg', 0.0, 1),
(2114, 'Ромашки в коробке', 65.00, 'Букет из ромашек в коробке', 'http://example.com/daisy8.jpg', 0.0, 1),
(2114, 'Ромашки с зеленью', 70.00, 'Букет из ромашек с зеленью', 'http://example.com/daisy9.jpg', 0.0, 1),
(2114, 'Ромашки и розы', 75.00, 'Букет из ромашек и роз', 'http://example.com/daisy10.jpg', 0.0, 1),

(2115, 'Белые лилии', 70.00, 'Букет из белых лилий', 'http://example.com/lily1.jpg', 0.0, 1),
(2115, 'Розовые лилии', 75.00, 'Букет из розовых лилий', 'http://example.com/lily2.jpg', 0.0, 1),
(2115, 'Желтые лилии', 80.00, 'Букет из желтых лилий', 'http://example.com/lily3.jpg', 0.0, 1),
(2115, 'Оранжевые лилии', 85.00, 'Букет из оранжевых лилий', 'http://example.com/lily4.jpg', 0.0, 1),
(2115, 'Красные лилии', 90.00, 'Букет из красных лилий', 'http://example.com/lily5.jpg', 0.0, 1),
(2115, 'Фиолетовые лилии', 95.00, 'Букет из фиолетовых лилий', 'http://example.com/lily6.jpg', 0.0, 1),
(2115, 'Многоцветные лилии', 100.00, 'Букет из многоцветных лилий', 'http://example.com/lily7.jpg', 0.0, 1),
(2115, 'Лилии в коробке', 105.00, 'Букет из лилий в коробке', 'http://example.com/lily8.jpg', 0.0, 1),
(2115, 'Лилии с зеленью', 110.00, 'Букет из лилий с зеленью', 'http://example.com/lily9.jpg', 0.0, 1),
(2115, 'Лилии и розы', 115.00, 'Букет из лилий и роз', 'http://example.com/lily10.jpg', 0.0, 1),

(2116, 'Голубые гортензии', 60.00, 'Букет из голубых гортензий', 'http://example.com/hydrangea1.jpg', 0.0, 1),
(2116, 'Розовые гортензии', 65.00, 'Букет из розовых гортензий', 'http://example.com/hydrangea2.jpg', 0.0, 1),
(2116, 'Белые гортензии', 70.00, 'Букет из белых гортензий', 'http://example.com/hydrangea3.jpg', 0.0, 1),
(2116, 'Фиолетовые гортензии', 75.00, 'Букет из фиолетовых гортензий', 'http://example.com/hydrangea4.jpg', 0.0, 1),
(2116, 'Многоцветные гортензии', 80.00, 'Букет из многоцветных гортензий', 'http://example.com/hydrangea5.jpg', 0.0, 1),
(2116, 'Гортензии в коробке', 85.00, 'Букет из гортензий в коробке', 'http://example.com/hydrangea6.jpg', 0.0, 1),
(2116, 'Гортензии с зеленью', 90.00, 'Букет из гортензий с зеленью', 'http://example.com/hydrangea7.jpg', 0.0, 1),
(2116, 'Гортензии и розы', 95.00, 'Букет из гортензий и роз', 'http://example.com/hydrangea8.jpg', 0.0, 1),
(2116, 'Гортензии и пионы', 100.00, 'Букет из гортензий и пионов', 'http://example.com/hydrangea9.jpg', 0.0, 1),
(2116, 'Гортензии и лилии', 105.00, 'Букет из гортензий и лилий', 'http://example.com/hydrangea10.jpg', 0.0, 1),

(2117, 'Синие ирисы', 50.00, 'Букет из синих ирисов', 'http://example.com/iris1.jpg', 0.0, 1),
(2117, 'Фиолетовые ирисы', 55.00, 'Букет из фиолетовых ирисов', 'http://example.com/iris2.jpg', 0.0, 1),
(2117, 'Белые ирисы', 60.00, 'Букет из белых ирисов', 'http://example.com/iris3.jpg', 0.0, 1),
(2117, 'Желтые ирисы', 65.00, 'Букет из желтых ирисов', 'http://example.com/iris4.jpg', 0.0, 1),
(2117, 'Розовые ирисы', 70.00, 'Букет из розовых ирисов', 'http://example.com/iris5.jpg', 0.0, 1),
(2117, 'Многоцветные ирисы', 75.00, 'Букет из многоцветных ирисов', 'http://example.com/iris6.jpg', 0.0, 1),
(2117, 'Ирисы в коробке', 80.00, 'Букет из ирисов в коробке', 'http://example.com/iris7.jpg', 0.0, 1),
(2117, 'Ирисы с зеленью', 85.00, 'Букет из ирисов с зеленью', 'http://example.com/iris8.jpg', 0.0, 1),
(2117, 'Ирисы и розы', 90.00, 'Букет из ирисов и роз', 'http://example.com/iris9.jpg', 0.0, 1),
(2117, 'Ирисы и лилии', 95.00, 'Букет из ирисов и лилий', 'http://example.com/iris10.jpg', 0.0, 1),

(2118, 'Белые нарциссы', 40.00, 'Букет из белых нарциссов', 'http://example.com/daffodil1.jpg', 0.0, 1),
(2118, 'Желтые нарциссы', 45.00, 'Букет из желтых нарциссов', 'http://example.com/daffodil2.jpg', 0.0, 1),
(2118, 'Оранжевые нарциссы', 50.00, 'Букет из оранжевых нарциссов', 'http://example.com/daffodil3.jpg', 0.0, 1),
(2118, 'Розовые нарциссы', 55.00, 'Букет из розовых нарциссов', 'http://example.com/daffodil4.jpg', 0.0, 1),
(2118, 'Многоцветные нарциссы', 60.00, 'Букет из многоцветных нарциссов', 'http://example.com/daffodil5.jpg', 0.0, 1),
(2118, 'Нарциссы в коробке', 65.00, 'Букет из нарциссов в коробке', 'http://example.com/daffodil6.jpg', 0.0, 1),
(2118, 'Нарциссы с зеленью', 70.00, 'Букет из нарциссов с зеленью', 'http://example.com/daffodil7.jpg', 0.0, 1),
(2118, 'Нарциссы и розы', 75.00, 'Букет из нарциссов и роз', 'http://example.com/daffodil8.jpg', 0.0, 1),
(2118, 'Нарциссы и лилии', 80.00, 'Букет из нарциссов и лилий', 'http://example.com/daffodil9.jpg', 0.0, 1),
(2118, 'Нарциссы и тюльпаны', 85.00, 'Букет из нарциссов и тюльпанов', 'http://example.com/daffodil10.jpg', 0.0, 1),

(2119, 'Розовые пионы', 70.00, 'Букет из розовых пионов', 'http://example.com/peony1.jpg', 0.0, 1),
(2119, 'Белые пионы', 75.00, 'Букет из белых пионов', 'http://example.com/peony2.jpg', 0.0, 1),
(2119, 'Красные пионы', 80.00, 'Букет из красных пионов', 'http://example.com/peony3.jpg', 0.0, 1),
(2119, 'Фиолетовые пионы', 85.00, 'Букет из фиолетовых пионов', 'http://example.com/peony4.jpg', 0.0, 1),
(2119, 'Многоцветные пионы', 90.00, 'Букет из многоцветных пионов', 'http://example.com/peony5.jpg', 0.0, 1),
(2119, 'Пионы в коробке', 95.00, 'Букет из пионов в коробке', 'http://example.com/peony6.jpg', 0.0, 1),
(2119, 'Пионы с зеленью', 100.00, 'Букет из пионов с зеленью', 'http://example.com/peony7.jpg', 0.0, 1),
(2119, 'Пионы и розы', 105.00, 'Букет из пионов и роз', 'http://example.com/peony8.jpg', 0.0, 1),
(2119, 'Пионы и лилии', 110.00, 'Букет из пионов и лилий', 'http://example.com/peony9.jpg', 0.0, 1),
(2119, 'Пионы и гортензии', 115.00, 'Букет из пионов и гортензий', 'http://example.com/peony10.jpg', 0.0, 1),

(2120, 'Белые эустомы', 60.00, 'Букет из белых эустом', 'http://example.com/eustoma1.jpg', 0.0, 1),
(2120, 'Розовые эустомы', 65.00, 'Букет из розовых эустом', 'http://example.com/eustoma2.jpg', 0.0, 1),
(2120, 'Фиолетовые эустомы', 70.00, 'Букет из фиолетовых эустом', 'http://example.com/eustoma3.jpg', 0.0, 1),
(2120, 'Желтые эустомы', 75.00, 'Букет из желтых эустом', 'http://example.com/eustoma4.jpg', 0.0, 1),
(2120, 'Многоцветные эустомы', 80.00, 'Букет из многоцветных эустом', 'http://example.com/eustoma5.jpg', 0.0, 1),
(2120, 'Эустомы в коробке', 85.00, 'Букет из эустом в коробке', 'http://example.com/eustoma6.jpg', 0.0, 1),
(2120, 'Эустомы с зеленью', 90.00, 'Букет из эустом с зеленью', 'http://example.com/eustoma7.jpg', 0.0, 1),
(2120, 'Эустомы и розы', 95.00, 'Букет из эустом и роз', 'http://example.com/eustoma8.jpg', 0.0, 1),
(2120, 'Эустомы и лилии', 100.00, 'Букет из эустом и лилий', 'http://example.com/eustoma9.jpg', 0.0, 1),
(2120, 'Эустомы и пионы', 105.00, 'Букет из эустом и пионов', 'http://example.com/eustoma10.jpg', 0.0, 1),

(2121, 'Траурный букет из роз', 80.00, 'Букет из темных роз', 'http://example.com/mourning1.jpg', 0.0, 1),
(2121, 'Траурный букет из лилий', 85.00, 'Букет из белых лилий', 'http://example.com/mourning2.jpg', 0.0, 1),
(2121, 'Траурный букет из хризантем', 75.00, 'Букет из белых хризантем', 'http://example.com/mourning3.jpg', 0.0, 1),
(2121, 'Траурный букет из гвоздик', 70.00, 'Букет из красных гвоздик', 'http://example.com/mourning4.jpg', 0.0, 1),
(2121, 'Траурный букет из роз и лилий', 90.00, 'Букет из роз и лилий', 'http://example.com/mourning5.jpg', 0.0, 1),
(2121, 'Траурный букет из роз и хризантем', 95.00, 'Букет из роз и хризантем', 'http://example.com/mourning6.jpg', 0.0, 1),
(2121, 'Траурный букет из роз и гвоздик', 100.00, 'Букет из роз и гвоздик', 'http://example.com/mourning7.jpg', 0.0, 1),
(2121, 'Траурный букет из лилий и хризантем', 85.00, 'Букет из лилий и хризантем', 'http://example.com/mourning8.jpg', 0.0, 1),
(2121, 'Траурный букет из гвоздик и хризантем', 80.00, 'Букет из гвоздик и хризантем', 'http://example.com/mourning9.jpg', 0.0, 1),
(2121, 'Траурный букет из роз, лилий и хризантем', 120.00, 'Букет из роз, лилий и хризантем', 'http://example.com/mourning10.jpg', 0.0, 1),

(2122, 'Искусственные розы', 50.00, 'Букет из искусственных роз', 'http://example.com/artificial1.jpg', 0.0, 1),
(2122, 'Искусственные лилии', 55.00, 'Букет из искусственных лилий', 'http://example.com/artificial2.jpg', 0.0, 1),
(2122, 'Искусственные тюльпаны', 60.00, 'Букет из искусственных тюльпанов', 'http://example.com/artificial3.jpg', 0.0, 1),
(2122, 'Искусственные хризантемы', 65.00, 'Букет из искусственных хризантем', 'http://example.com/artificial4.jpg', 0.0, 1),
(2122, 'Искусственные пионы', 70.00, 'Букет из искусственных пионов', 'http://example.com/artificial5.jpg', 0.0, 1),
(2122, 'Искусственные гортензии', 75.00, 'Букет из искусственных гортензий', 'http://example.com/artificial6.jpg', 0.0, 1),
(2122, 'Искусственные ирисы', 80.00, 'Букет из искусственных ирисов', 'http://example.com/artificial7.jpg', 0.0, 1),
(2122, 'Искусственные нарциссы', 85.00, 'Букет из искусственных нарциссов', 'http://example.com/artificial8.jpg', 0.0, 1),
(2122, 'Искусственные эустомы', 90.00, 'Букет из искусственных эустом', 'http://example.com/artificial9.jpg', 0.0, 1),
(2122, 'Искусственные цветы в коробке', 100.00, 'Букет из искусственных цветов в коробке', 'http://example.com/artificial10.jpg', 0.0, 1)
]