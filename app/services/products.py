import math
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import InventoryBatch
from app.domain.fuzzy import STORAGE_LOCATIONS, STORAGE_SHORT_LABELS, urgency, urgency_label, urgency_reason


def validate_product_input(name, quantity, opened_on, today=None):
    today = today or date.today()
    if not name.strip():
        raise ValueError("Назва продукту не може бути порожньою.")
    if not math.isfinite(quantity) or quantity <= 0:
        raise ValueError("Кількість продукту має бути більшою за нуль.")
    if opened_on is not None and opened_on > today:
        raise ValueError("Дата відкриття не може бути в майбутньому.")


def product_rows(db: Session, storage=None):
    statement = select(InventoryBatch).options(selectinload(InventoryBatch.ingredient))
    if storage in STORAGE_LOCATIONS:
        statement = statement.where(InventoryBatch.storage_location == storage)

    groups = {}
    for batch in db.scalars(statement):
        ingredient = batch.ingredient
        current_urgency = urgency(
            batch.expires_on,
            batch.opened_on,
            ingredient.default_category,
            storage_location=batch.storage_location,
        )
        batch_view = {
            "id": batch.id,
            "quantity": batch.quantity,
            "unit": batch.unit,
            "expires_on": batch.expires_on,
            "opened_on": batch.opened_on,
            "days": (batch.expires_on - date.today()).days,
            "u": current_urgency,
            "reason": urgency_reason(
                batch.expires_on,
                batch.opened_on,
                ingredient.default_category,
                batch.storage_location,
            ),
            "storage_label": STORAGE_SHORT_LABELS.get(batch.storage_location, batch.storage_location),
        }
        group = groups.setdefault(ingredient.id, {
            "ingredient": ingredient,
            "quantity": 0,
            "unit": batch.unit,
            "u": 0.0,
            "label": "Є час",
            "reason": "",
            "storage_label": batch_view["storage_label"],
            "batches": [],
        })
        group["quantity"] += batch.quantity
        group["u"] = max(group["u"], current_urgency)
        group["batches"].append(batch_view)
        if current_urgency >= group["u"]:
            group["reason"] = batch_view["reason"]
            group["storage_label"] = batch_view["storage_label"]

    rows = []
    for group in groups.values():
        group["batches"].sort(key=lambda batch: (-batch["u"], batch["expires_on"], batch["id"]))
        storage_locations = {batch["storage_label"] for batch in group["batches"]}
        group["storage_label"] = (
            next(iter(storage_locations)) if len(storage_locations) == 1 else "Різні"
        )
        group["label"] = urgency_label(group["u"])
        rows.append(group)
    return sorted(rows, key=lambda row: -row["u"])


def product_stats(rows):
    return {
        "total": len(rows),
        "urgent": sum(row["u"] >= 0.7 for row in rows),
        "soon": sum(0.35 <= row["u"] < 0.7 for row in rows),
    }
