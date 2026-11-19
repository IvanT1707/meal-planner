from datetime import date, timedelta
from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import Base, Product, SessionLocal, engine
from .fuzzy import CATEGORIES, urgency, urgency_label
from .planner import plan_week
from .recipes import RECIPES

app = FastAPI(title="Планувальник раціону")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
Base.metadata.create_all(engine)

WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def product_rows(db: Session):
    rows = []
    for p in db.scalars(select(Product)):
        u = urgency(p.expires_on, p.opened_on, p.category)
        rows.append({"p": p, "u": u, "label": urgency_label(u), "days": (p.expires_on - date.today()).days})
    return sorted(rows, key=lambda r: -r["u"])


def products_response(request: Request, db: Session):
    return templates.TemplateResponse(request, "partials/_products.html", {"rows": product_rows(db)})


@app.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    ctx = {"rows": product_rows(db), "categories": CATEGORIES, "today": date.today().isoformat()}
    return templates.TemplateResponse(request, "index.html", ctx)


@app.post("/products")
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


@app.delete("/products/{product_id}")
def delete_product(product_id: int, request: Request, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product:
        db.delete(product)
        db.commit()
    return products_response(request, db)


@app.post("/demo")
def load_demo(request: Request, db: Session = Depends(get_db)):
    today = date.today()
    for name, cat, qty, unit, days, opened_ago in DEMO:
        db.add(Product(
            name=name, category=cat, quantity=qty, unit=unit, expires_on=today + timedelta(days=days),
            opened_on=today - timedelta(days=opened_ago) if opened_ago is not None else None,
        ))
    db.commit()
    return products_response(request, db)


@app.get("/plan")
def plan(request: Request, db: Session = Depends(get_db)):
    stock = {r["p"].name: (r["p"].quantity, r["p"].unit, r["u"]) for r in product_rows(db)}
    days, shopping = plan_week(RECIPES, stock, days=7)
    labelled = [(f"{WEEKDAYS[(date.today() + timedelta(d)).weekday()]} {(date.today() + timedelta(d)):%d.%m}", day)
                for d, day in enumerate(days)]
    return templates.TemplateResponse(request, "partials/_plan.html", {"days": labelled, "shopping": shopping})
