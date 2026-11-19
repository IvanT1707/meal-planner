from datetime import date

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(30), default="produce_hard")
    quantity: Mapped[float]
    unit: Mapped[str] = mapped_column(String(10))
    expires_on: Mapped[date]
    opened_on: Mapped[date | None] = mapped_column(default=None)
