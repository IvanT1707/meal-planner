import math
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Product
from app.domain.fuzzy import STORAGE_SHORT_LABELS, STORAGE_LOCATIONS, urgency, urgency_label, urgency_reason


def validate_product_input(name, quantity, opened_on, today=None):
    today = today or date.today()
    if not name.strip():
        raise ValueError("Назва продукту не може бути порожньою.")
    if not math.isfinite(quantity) or quantity <= 0:
        raise ValueError("Кількість продукту має бути більшою за нуль.")
    if opened_on is not None and opened_on > today:
        raise ValueError("Дата відкриття не може бути в майбутньому.")


def product_rows(db: Session, storage=None):
    statement = select(Product)
    if storage in STORAGE_LOCATIONS:
        statement = statement.where(Product.storage_location == storage)

    rows = []
    for product in db.scalars(statement):
        current_urgency = urgency(
            product.expires_on,
            product.opened_on,
            product.category,
            storage_location=product.storage_location,
        )
        rows.append({
            "p": product,
            "u": current_urgency,
            "label": urgency_label(current_urgency),
            "reason": urgency_reason(
                product.expires_on,
                product.opened_on,
                product.category,
                product.storage_location,
            ),
            "days": (product.expires_on - date.today()).days,
            "storage_label": STORAGE_SHORT_LABELS.get(product.storage_location, product.storage_location),
        })
    return sorted(rows, key=lambda row: -row["u"])


def product_stats(rows):
    return {
        "total": len(rows),
        "urgent": sum(row["u"] >= 0.7 for row in rows),
        "soon": sum(0.35 <= row["u"] < 0.7 for row in rows),
    }
