from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InventoryBatch(Base):
    __tablename__ = "inventory_batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"), index=True)
    storage_location: Mapped[str] = mapped_column(String(20), default="fridge")
    quantity: Mapped[float]
    unit: Mapped[str] = mapped_column(String(10))
    expires_on: Mapped[date]
    opened_on: Mapped[date | None] = mapped_column(default=None)
    purchased_on: Mapped[date] = mapped_column(default=date.today)

    ingredient = relationship("Ingredient", back_populates="batches")
