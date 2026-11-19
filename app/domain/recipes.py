"""Локальний каталог повсякденних рецептів."""

BREAKFAST = ["breakfast"]
LUNCH = ["lunch"]
DINNER = ["dinner"]
LUNCH_OR_DINNER = ["lunch", "dinner"]

RECIPES = [
    {"name": "Омлет з молоком", "meal_types": BREAKFAST, "servings": 1, "keeps_days": 1,
     "ingredients": {"яйця": (3, "шт"), "молоко": (100, "мл")}},
    {"name": "Сирники", "meal_types": BREAKFAST, "servings": 1, "keeps_days": 1,
     "ingredients": {"сир кисломолочний": (250, "г"), "яйця": (1, "шт"), "борошно": (60, "г")}},
    {"name": "Млинці", "meal_types": BREAKFAST, "servings": 2, "keeps_days": 2,
     "ingredients": {"молоко": (300, "мл"), "яйця": (2, "шт"), "борошно": (150, "г")}},
    {"name": "Вівсянка з яблуком", "meal_types": BREAKFAST, "servings": 1, "keeps_days": 1,
     "ingredients": {"вівсянка": (80, "г"), "молоко": (150, "мл"), "яблука": (1, "шт")}},
    {"name": "Яєчня з томатами", "meal_types": BREAKFAST, "servings": 1, "keeps_days": 1,
     "ingredients": {"яйця": (2, "шт"), "томати": (150, "г")}},
    {"name": "Тости з сиром", "meal_types": BREAKFAST, "servings": 1, "keeps_days": 1,
     "ingredients": {"хліб": (2, "шт"), "сир твердий": (50, "г")}},
    {"name": "Йогурт з фруктами", "meal_types": BREAKFAST, "servings": 1, "keeps_days": 1,
     "ingredients": {"йогурт": (200, "г"), "яблука": (1, "шт")}},
    {"name": "Борщ", "meal_types": LUNCH, "servings": 4, "keeps_days": 3,
     "ingredients": {"буряк": (2, "шт"), "капуста": (800, "г"), "картопля": (12, "шт"), "морква": (4, "шт")}},
    {"name": "Курячий суп", "meal_types": LUNCH, "servings": 4, "keeps_days": 3,
     "ingredients": {"курка": (600, "г"), "картопля": (8, "шт"), "морква": (2, "шт"), "цибуля": (2, "шт")}},
    {"name": "Чечевичне рагу", "meal_types": LUNCH_OR_DINNER, "servings": 3, "keeps_days": 3,
     "ingredients": {"чечевиця": (300, "г"), "морква": (2, "шт"), "томати": (300, "г"), "цибуля": (1, "шт")}},
    {"name": "Гречка з грибами", "meal_types": LUNCH_OR_DINNER, "servings": 2, "keeps_days": 2,
     "ingredients": {"гречка": (300, "г"), "гриби": (400, "г"), "цибуля": (2, "шт")}},
    {"name": "Паста з томатним соусом", "meal_types": LUNCH_OR_DINNER, "servings": 2, "keeps_days": 2,
     "ingredients": {"макарони": (400, "г"), "томати": (600, "г"), "цибуля": (1, "шт")}},
    {"name": "Курка з овочами", "meal_types": LUNCH_OR_DINNER, "servings": 3, "keeps_days": 3,
     "ingredients": {"курка": (900, "г"), "морква": (3, "шт"), "цибуля": (2, "шт"), "картопля": (9, "шт")}},
    {"name": "Рис з овочами", "meal_types": LUNCH_OR_DINNER, "servings": 2, "keeps_days": 2,
     "ingredients": {"рис": (300, "г"), "морква": (2, "шт"), "томати": (200, "г")}},
    {"name": "Квасоля з овочами", "meal_types": LUNCH_OR_DINNER, "servings": 3, "keeps_days": 3,
     "ingredients": {"квасоля": (300, "г"), "томати": (300, "г"), "цибуля": (2, "шт")}},
    {"name": "Запечена курка з картоплею", "meal_types": DINNER, "servings": 3, "keeps_days": 3,
     "ingredients": {"курка": (1000, "г"), "картопля": (12, "шт"), "сметана": (180, "г")}},
    {"name": "Картопляне пюре", "meal_types": DINNER, "servings": 1, "keeps_days": 1,
     "ingredients": {"картопля": (5, "шт"), "молоко": (100, "мл")}},
    {"name": "Овочевий салат", "meal_types": DINNER, "servings": 1, "keeps_days": 1,
     "ingredients": {"огірки": (2, "шт"), "томати": (200, "г"), "сметана": (50, "г")}},
    {"name": "Риба з овочами", "meal_types": DINNER, "servings": 2, "keeps_days": 2,
     "ingredients": {"риба": (500, "г"), "морква": (2, "шт"), "картопля": (4, "шт")}},
    {"name": "Тушковані овочі", "meal_types": LUNCH_OR_DINNER, "servings": 2, "keeps_days": 2,
     "ingredients": {"картопля": (4, "шт"), "морква": (2, "шт"), "томати": (200, "г"), "цибуля": (1, "шт")}},
]
