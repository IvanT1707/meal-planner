from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    default_category: Mapped[str] = mapped_column(String(30), default="produce_hard")
    default_unit: Mapped[str] = mapped_column(String(10), default="шт")

    batches = relationship("InventoryBatch", back_populates="ingredient")
