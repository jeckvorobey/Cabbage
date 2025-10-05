"""Импорт моделей для регистрации в метаданных SQLAlchemy (Alembic autogenerate).

Важно: импортируем все модули, чтобы Alembic видел таблицы.
"""
from .user import Address, User, UserRole  # noqa: F401
from .catalog import Category, Unit, Product, Price  # noqa: F401
from .order import Order, OrderItem, OrderStatus  # noqa: F401
from .cart import Cart, CartItem  # noqa: F401
