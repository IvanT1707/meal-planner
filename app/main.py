from fastapi import FastAPI

from app.api.routes import pages, planning, products
from app.db import Base, SessionLocal, engine
from app.db.models import Ingredient, InventoryBatch  # noqa: F401 - registers models with Base
from app.db.seed import seed_ingredients


app = FastAPI(title="Планувальник раціону")
Base.metadata.create_all(engine)
with SessionLocal() as db:
    seed_ingredients(db)
    db.commit()

app.include_router(pages.router)
app.include_router(products.router)
app.include_router(planning.router)
