from fastapi import FastAPI

from app.api.routes import pages, planning, products
from app.db import Base, engine
from app.db.models import Product  # noqa: F401 - registers the model with Base


app = FastAPI(title="Планувальник раціону")
Base.metadata.create_all(engine)

app.include_router(pages.router)
app.include_router(products.router)
app.include_router(planning.router)
