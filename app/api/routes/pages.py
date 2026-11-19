from datetime import date

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.templates import templates
from app.db import get_db
from app.db.models import Ingredient
from app.domain.fuzzy import CATEGORIES, PRODUCT_CATEGORIES, STORAGE_LOCATIONS
from app.services.products import product_rows, product_stats


router = APIRouter()


@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    rows = product_rows(db)
    ingredients = db.scalars(select(Ingredient).order_by(Ingredient.name)).all()
    context = {
        "rows": rows,
        "stats": product_stats(rows),
        "ingredients": ingredients,
        "categories": CATEGORIES,
        "category_options": PRODUCT_CATEGORIES,
        "storage_locations": STORAGE_LOCATIONS,
        "today": date.today().isoformat(),
    }
    return templates.TemplateResponse(request, "index.html", context)
