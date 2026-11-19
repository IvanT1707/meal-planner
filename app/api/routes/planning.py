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


@router.get("/plan")
def plan(request: Request, db: Session = Depends(get_db)):
    stock = {
        row["p"].name: (row["p"].quantity, row["p"].unit, row["u"])
        for row in product_rows(db)
    }
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
