from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, BigInteger, func, Boolean, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    created: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

# Категории
class Category(Base):
    __tablename__ = 'category'

    category_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

# Букеты
class Bouquet(Base):
    __tablename__ = 'bouquets'

    bouquet_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    image_url: Mapped[str] = mapped_column(String(150))
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id', ondelete='CASCADE'), nullable=False)
    available: Mapped[int] = mapped_column(Boolean, default=True, nullable=False)
    discount: Mapped[int] = mapped_column(Float, default=0)

# Пользователи
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    username: Mapped[str] = mapped_column(String(150), nullable=True)
    phone: Mapped[str] = mapped_column(String(13), nullable=True)

# Корзина
class Cart(Base):
    __tablename__ = 'cart'

    cart_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    bouquet_id: Mapped[int] = mapped_column(ForeignKey('bouquets.id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int] = mapped_column(default=1)

    user: Mapped['User'] = relationship(backref='cart')
    bouquet: Mapped['Bouquet'] = relationship(backref='cart')

# Акции
class Promotion(Base):
    __tablename__ = 'promotions'

    promotion_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    discount: Mapped[float] = mapped_column(Numeric(5, 2), default=0)

# Заказы
class Order(Base):
    __tablename__ = 'orders'

    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    delivery_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default='pending')

    user: Mapped['User'] = relationship(backref='orders')