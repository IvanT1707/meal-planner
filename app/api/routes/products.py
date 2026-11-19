from datetime import date, timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.templates import templates
from app.db import get_db
from app.db.models import Ingredient, InventoryBatch
from app.domain.demo import DEMO
from app.domain.fuzzy import CATEGORY_CONFIG, STORAGE_LOCATIONS
from app.services.products import product_rows, product_stats, validate_product_input


router = APIRouter()


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
    ingredient_id: int = Form(...),
    quantity: float = Form(...),
    expires_on: date = Form(...),
    opened_on: str = Form(""),
    storage_location: str | None = Form(None),
    db: Session = Depends(get_db),
):
    ingredient = db.get(Ingredient, ingredient_id)
    if ingredient is None:
        raise HTTPException(status_code=422, detail="Обраного інгредієнта не існує в каталозі.")

    opened_date = None
    if opened_on:
        try:
            opened_date = date.fromisoformat(opened_on)
        except ValueError as error:
            raise HTTPException(status_code=422, detail="Дата відкриття має бути коректною датою.") from error
    try:
        validate_product_input(ingredient.name, quantity, opened_date)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    recommended_storage = CATEGORY_CONFIG.get(
        ingredient.default_category,
        CATEGORY_CONFIG["produce_hard"],
    ).recommended_storage
    selected_storage = storage_location if storage_location in STORAGE_LOCATIONS else recommended_storage
    db.add(InventoryBatch(
        ingredient_id=ingredient.id,
        storage_location=selected_storage,
        quantity=quantity,
        unit=ingredient.default_unit,
        expires_on=expires_on,
        opened_on=opened_date,
    ))
    db.commit()
    return products_response(request, db)


@router.delete("/products/{batch_id}")
def delete_product(batch_id: int, request: Request, db: Session = Depends(get_db)):
    batch = db.get(InventoryBatch, batch_id)
    if batch:
        db.delete(batch)
        db.commit()
    return products_response(request, db)


@router.post("/demo")
def load_demo(request: Request, db: Session = Depends(get_db)):
    today = date.today()
    db.query(InventoryBatch).delete()
    ingredients = {
        ingredient.name: ingredient
        for ingredient in db.scalars(select(Ingredient))
    }
    for name, category, storage_location, quantity, unit, days, opened_ago in DEMO:
        ingredient = ingredients.get(name)
        if ingredient is None:
            raise HTTPException(status_code=500, detail=f"Інгредієнт «{name}» відсутній у каталозі.")
        db.add(InventoryBatch(
            ingredient_id=ingredient.id,
            storage_location=storage_location,
            quantity=quantity,
            unit=unit,
            expires_on=today + timedelta(days=days),
            opened_on=today - timedelta(days=opened_ago) if opened_ago is not None else None,
        ))
    db.commit()
    return products_response(request, db)
