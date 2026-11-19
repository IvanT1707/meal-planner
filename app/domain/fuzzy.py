"""Нечітка оцінка терміновості використання продукту.

Категорії спираються на орієнтири USDA FoodKeeper щодо безпечного зберігання
після відкриття упаковки: https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/food-keeper-app

Система типу Сугено нульового порядку: входи фазифікуються функціями належності,
правила «якщо-то» спрацьовують з силою min(...), вихід дефазифікується зваженим
середнім. Результат: від 0 (є час) до 1 (терміново).
"""
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ProductCategory:
    key: str
    label: str
    max_open_days: int
    perishability_factor: float
    recommended_storage: str


# 14 днів — нейтральна шкала для терміну на упаковці. Коротший FoodKeeper-
# орієнтир робить однакову кількість днів до expiry більш терміновою.
_REFERENCE_OPEN_DAYS = 14
PRODUCT_CATEGORIES = (
    ProductCategory("meat_fish", "М'ясо, птиця та риба", 2, 2 / _REFERENCE_OPEN_DAYS, "fridge"),
    ProductCategory("dairy", "Молочні продукти та яйця", 4, 4 / _REFERENCE_OPEN_DAYS, "fridge"),
    ProductCategory("produce_soft", "Швидкопсувні овочі, зелень, гриби, ягоди", 3, 3 / _REFERENCE_OPEN_DAYS, "fridge"),
    ProductCategory("produce_hard", "Тверді овочі та фрукти", 14, 1.0, "pantry"),
    ProductCategory("bakery", "Хлібобулочні вироби", 4, 4 / _REFERENCE_OPEN_DAYS, "pantry"),
    ProductCategory("prepared", "Готові страви та відкриті соуси", 4, 4 / _REFERENCE_OPEN_DAYS, "fridge"),
    ProductCategory("pantry", "Бакалія: крупи, борошно, макарони", 60, 60 / _REFERENCE_OPEN_DAYS, "pantry"),
)
CATEGORY_CONFIG = {category.key: category for category in PRODUCT_CATEGORIES}
CATEGORIES = {category.key: category.label for category in PRODUCT_CATEGORIES}
DEFAULT_CATEGORY = "produce_hard"
STORAGE_LOCATIONS = {
    "fridge": "Холодильник",
    "freezer": "Морозильна камера",
    "pantry": "Комора / кімнатна температура",
}
FREEZER_SPOILAGE_RATE = 0.1
ROOM_TEMPERATURE_CRITICAL_CATEGORIES = {"meat_fish", "dairy", "prepared"}


def _up(x, a, b):
    if x <= a:
        return 0.0
    if x >= b:
        return 1.0
    return (x - a) / (b - a)


def _down(x, a, b):
    return 1.0 - _up(x, a, b)


def _tri(x, a, b, c):
    return min(_up(x, a, b), _down(x, b, c))


# (терм днів, терм відкриття, вихід правила); None = «будь-який»
RULES = [
    ("critical", None, 1.00),
    ("soon", "not_opened", 0.55),
    ("soon", "recent", 0.75),
    ("soon", "long", 0.90),
    ("plenty", "not_opened", 0.05),
    ("plenty", "recent", 0.20),
    ("plenty", "long", 0.55),
    ("any", "expired", 1.00),
]


def _day_terms(e):
    return {"critical": _down(e, 1, 3), "soon": _tri(e, 1, 4, 8), "plenty": _up(e, 4, 9)}


def _open_terms(days_open, max_open_days):
    if days_open is None:
        return {"not_opened": 1.0, "recent": 0.0, "long": 0.0, "expired": 0.0}

    share = max(days_open, 0) / max_open_days
    return {
        "not_opened": 0.0,
        "recent": _down(share, 0.15, 0.45),
        "long": _up(share, 0.25, 0.75),
        "expired": _up(share, 0.75, 0.9),
    }


def urgency(expires_on, opened_on=None, category=DEFAULT_CATEGORY, today=None, storage_location=None):
    today = today or date.today()
    category_config = CATEGORY_CONFIG.get(category, CATEGORY_CONFIG[DEFAULT_CATEGORY])
    storage_location = storage_location or category_config.recommended_storage
    if category in ROOM_TEMPERATURE_CRITICAL_CATEGORIES and storage_location == "pantry":
        return 1.0

    days_open = (today - opened_on).days if opened_on else None
    storage_rate = FREEZER_SPOILAGE_RATE if storage_location == "freezer" else 1.0
    if days_open is not None:
        open_share = days_open * storage_rate / category_config.max_open_days
        if open_share >= 0.9:
            return 1.0

    effective = (
        (expires_on - today).days
        * category_config.perishability_factor
        / storage_rate
    )
    effective_days_open = days_open * storage_rate if days_open is not None else None
    d, o = _day_terms(effective), _open_terms(effective_days_open, category_config.max_open_days)

    num = den = 0.0
    for day_term, open_term, out in RULES:
        day_strength = 1.0 if day_term == "any" else d[day_term]
        strength = day_strength if open_term is None else min(day_strength, o[open_term])
        num += strength * out
        den += strength
    return round(num / den, 3) if den else 0.0


def urgency_label(u):
    if u >= 0.7:
        return "Терміново"
    if u >= 0.35:
        return "Скоро"
    return "Є час"
