from datetime import date, timedelta

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.templates import templates
from app.db import get_db
from app.domain.planner import plan_week
from app.domain.recipes import RECIPES
from app.services.products import product_rows


router = APIRouter()
WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
MEAL_LABELS = {"breakfast": "Сніданок", "lunch": "Обід", "dinner": "Вечеря"}


def aggregate_stock(rows):
    grouped = {}
    for row in rows:
        product = row["p"]
        key = (product.name, product.unit)
        if key not in grouped:
            grouped[key] = [0, row["u"]]
        grouped[key][0] += product.quantity
        grouped[key][1] = max(grouped[key][1], row["u"])

    stock = {}
    for (name, unit), (quantity, current_urgency) in grouped.items():
        existing = stock.get(name)
        if existing is None or existing[1] == unit:
            if existing is None:
                stock[name] = (quantity, unit, current_urgency)
            else:
                stock[name] = (
                    existing[0] + quantity,
                    unit,
                    max(existing[2], current_urgency),
                )
        elif current_urgency > existing[2]:
            stock[name] = (quantity, unit, current_urgency)
    return stock


@router.get("/plan")
def plan(request: Request, db: Session = Depends(get_db)):
    stock = aggregate_stock(product_rows(db))
    days, shopping = plan_week(RECIPES, stock, days=7)
    labelled = [
        (
            f"{WEEKDAYS[(date.today() + timedelta(day)).weekday()]} "
            f"{date.today() + timedelta(day):%d.%m}",
            day_plan,
        )
        for day, day_plan in enumerate(days)
    ]
    return templates.TemplateResponse(
        request,
        "partials/_plan.html",
        {"days": labelled, "shopping": shopping, "meal_labels": MEAL_LABELS},
    )
