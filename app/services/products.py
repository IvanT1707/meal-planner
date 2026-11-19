from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Product
from app.domain.fuzzy import STORAGE_SHORT_LABELS, urgency, urgency_label, urgency_reason


def product_rows(db: Session):
    rows = []
    for product in db.scalars(select(Product)):
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
