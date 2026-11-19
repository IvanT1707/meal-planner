import os
from datetime import date

from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# За замовчуванням SQLite (запуск без налаштувань). Для PostgreSQL:
# DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/meal_planner
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fridge.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(10), default="medium")
    quantity: Mapped[float]
    unit: Mapped[str] = mapped_column(String(10))
    expires_on: Mapped[date]
    opened_on: Mapped[date | None] = mapped_column(default=None)
