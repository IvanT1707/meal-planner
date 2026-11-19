from datetime import date, timedelta

from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session

from app.core.templates import templates
from app.db import get_db
from app.db.models import Product
from app.services.products import product_rows


router = APIRouter()

# назва, категорія, кількість, одиниця, днів до кінця терміну, днів тому відкрито
DEMO = [
    ("молоко", "fast", 500, "мл", 2, 1), ("яйця", "fast", 6, "шт", 6, None),
    ("сир кисломолочний", "fast", 300, "г", 3, None), ("курка", "fast", 500, "г", 1, None),
    ("гриби", "fast", 250, "г", 2, None), ("сметана", "fast", 200, "г", 5, 3),
    ("картопля", "medium", 8, "шт", 20, None), ("морква", "medium", 4, "шт", 10, None),
    ("цибуля", "medium", 3, "шт", 30, None), ("томати", "medium", 400, "г", 4, None),
    ("огірки", "medium", 2, "шт", 4, None), ("гречка", "slow", 500, "г", 200, None),
    ("борошно", "slow", 1000, "г", 150, None),
]


def products_response(request: Request, db: Session):
    return templates.TemplateResponse(request, "partials/_products.html", {"rows": product_rows(db)})


@router.post("/products")
def add_product(
    request: Request,
    name: str = Form(...), category: str = Form("medium"), quantity: float = Form(...),
    unit: str = Form("шт"), expires_on: date = Form(...), opened_on: str = Form(""),
    db: Session = Depends(get_db),
):
    db.add(Product(
        name=name.strip().lower(), category=category, quantity=quantity, unit=unit.strip(),
        expires_on=expires_on, opened_on=date.fromisoformat(opened_on) if opened_on else None,
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
    for name, category, quantity, unit, days, opened_ago in DEMO:
        db.add(Product(
            name=name, category=category, quantity=quantity, unit=unit,
            expires_on=today + timedelta(days=days),
            opened_on=today - timedelta(days=opened_ago) if opened_ago is not None else None,
        ))
    db.commit()
    return products_response(request, db)
