from datetime import date

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.templates import templates
from app.db import get_db
from app.domain.fuzzy import CATEGORIES
from app.services.products import product_rows


router = APIRouter()


@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    context = {
        "rows": product_rows(db),
        "categories": CATEGORIES,
        "today": date.today().isoformat(),
    }
    return templates.TemplateResponse(request, "index.html", context)
