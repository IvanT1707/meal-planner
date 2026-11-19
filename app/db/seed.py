from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Ingredient
from app.domain.demo import DEMO
from app.domain.fuzzy import DEFAULT_CATEGORY
from app.domain.recipes import RECIPES

RECIPE_CATEGORY_DEFAULTS = {
    "курка": "meat_fish",
    "риба": "meat_fish",
    "молоко": "dairy",
    "йогурт": "dairy",
    "сир": "dairy",
    "сир кисломолочний": "dairy",
    "сир твердий": "dairy",
    "сметана": "dairy",
    "яйця": "dairy",
    "гриби": "produce_soft",
    "томати": "produce_soft",
    "огірки": "produce_soft",
    "яблука": "produce_hard",
    "морква": "produce_hard",
    "цибуля": "produce_hard",
    "картопля": "produce_hard",
    "буряк": "produce_hard",
    "капуста": "produce_hard",
    "хліб": "bakery",
    "вівсянка": "pantry",
    "гречка": "pantry",
    "рис": "pantry",
    "макарони": "pantry",
    "борошно": "pantry",
    "чечевиця": "pantry",
    "квасоля": "pantry",
}


def _ingredient_defaults():
    defaults = {}
    for recipe in RECIPES:
        for name, (_, unit) in recipe["ingredients"].items():
            defaults.setdefault(name, {
                "default_category": RECIPE_CATEGORY_DEFAULTS.get(name, DEFAULT_CATEGORY),
                "default_unit": unit,
            })

    for name, category, _, _, unit, _, _ in DEMO:
        defaults[name] = {
            "default_category": category,
            "default_unit": unit,
        }
    return defaults


def seed_ingredients(db: Session):
    for name, values in _ingredient_defaults().items():
        ingredient = db.scalar(select(Ingredient).where(Ingredient.name == name))
        if ingredient is None:
            db.add(Ingredient(name=name, **values))
        else:
            ingredient.default_category = values["default_category"]
            ingredient.default_unit = values["default_unit"]
