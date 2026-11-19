from datetime import date

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.templates import templates
from app.db import get_db
from app.domain.fuzzy import CATEGORIES, PRODUCT_CATEGORIES, STORAGE_LOCATIONS
from app.services.products import product_rows, product_stats


router = APIRouter()


@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    rows = product_rows(db)
    context = {
        "rows": rows,
        "stats": product_stats(rows),
        "categories": CATEGORIES,
        "category_options": PRODUCT_CATEGORIES,
        "storage_locations": STORAGE_LOCATIONS,
        "today": date.today().isoformat(),
    }
    return templates.TemplateResponse(request, "index.html", context)
