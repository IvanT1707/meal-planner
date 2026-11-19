from datetime import date, timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.templates import templates
from app.db import get_db
from app.db.models import Product
from app.domain.fuzzy import CATEGORY_CONFIG, STORAGE_LOCATIONS
from app.services.products import product_rows, product_stats, validate_product_input


router = APIRouter()

# назва, категорія, кількість, одиниця, днів до кінця терміну, днів тому відкрито
DEMO = [
    ("молоко", "dairy", "fridge", 500, "мл", 2, 1), ("яйця", "dairy", "fridge", 6, "шт", 6, None),
    ("сир кисломолочний", "dairy", "fridge", 300, "г", 3, None), ("курка", "meat_fish", "fridge", 500, "г", 1, None),
    ("гриби", "produce_soft", "fridge", 250, "г", 2, None), ("сметана", "dairy", "fridge", 200, "г", 5, 3),
    ("картопля", "produce_hard", "pantry", 8, "шт", 20, None), ("морква", "produce_hard", "pantry", 4, "шт", 10, None),
    ("цибуля", "produce_hard", "pantry", 3, "шт", 30, None), ("томати", "produce_soft", "fridge", 400, "г", 4, None),
    ("огірки", "produce_soft", "fridge", 2, "шт", 4, None), ("гречка", "pantry", "pantry", 500, "г", 200, None),
    ("борошно", "pantry", "pantry", 1000, "г", 150, None),
]


def products_response(request: Request, db: Session, storage=None):
    rows = product_rows(db, storage)
    return templates.TemplateResponse(
        request,
        "partials/_products.html",
        {"rows": rows, "stats": product_stats(rows)},
    )


@router.get("/products")
def list_products(request: Request, storage: str | None = None, db: Session = Depends(get_db)):
    return products_response(request, db, storage)


@router.post("/products")
def add_product(
    request: Request,
    name: str = Form(...), category: str = Form("produce_hard"), quantity: float = Form(...),
    unit: str = Form("шт"), expires_on: date = Form(...), opened_on: str = Form(""),
    storage_location: str | None = Form(None),
    db: Session = Depends(get_db),
):
    opened_date = None
    if opened_on:
        try:
            opened_date = date.fromisoformat(opened_on)
        except ValueError as error:
            raise HTTPException(status_code=422, detail="Дата відкриття має бути коректною датою.") from error
    try:
        validate_product_input(name, quantity, opened_date)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    recommended_storage = CATEGORY_CONFIG.get(category, CATEGORY_CONFIG["produce_hard"]).recommended_storage
    selected_storage = storage_location if storage_location in STORAGE_LOCATIONS else recommended_storage
    db.add(Product(
        name=name.strip().lower(), category=category, quantity=quantity, unit=unit.strip(),
        expires_on=expires_on, opened_on=opened_date,
        storage_location=selected_storage,
    ))
    db.commit()
    return products_response(request, db)


@router.delete("/products/{product_id}")
def delete_product(product_id: int, request: Request, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product:
        db.delete(product)
        db.commit()
    return products_response(request, db)


@router.post("/demo")
def load_demo(request: Request, db: Session = Depends(get_db)):
    today = date.today()
    db.query(Product).delete()
    for name, category, storage_location, quantity, unit, days, opened_ago in DEMO:
        db.add(Product(
            name=name, category=category, storage_location=storage_location, quantity=quantity, unit=unit,
            expires_on=today + timedelta(days=days),
            opened_on=today - timedelta(days=opened_ago) if opened_ago is not None else None,
        ))
    db.commit()
    return products_response(request, db)
