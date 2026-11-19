from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Product
from app.domain.fuzzy import urgency, urgency_label


def product_rows(db: Session):
    rows = []
    for product in db.scalars(select(Product)):
        current_urgency = urgency(product.expires_on, product.opened_on, product.category)
        rows.append({
            "p": product,
            "u": current_urgency,
            "label": urgency_label(current_urgency),
            "days": (product.expires_on - date.today()).days,
        })
    return sorted(rows, key=lambda row: -row["u"])
