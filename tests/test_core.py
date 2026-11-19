from datetime import date, timedelta

from app.domain.fuzzy import (
    CATEGORIES,
    CATEGORY_CONFIG,
    STORAGE_LOCATIONS,
    urgency,
    urgency_label,
    urgency_reason,
)
from app.domain.planner import plan_week
from app.domain.recipes import RECIPES

TODAY = date(2026, 1, 10)


def u(days, opened_ago=None, cat="produce_hard"):
    opened = TODAY - timedelta(days=opened_ago) if opened_ago is not None else None
    return urgency(TODAY + timedelta(days=days), opened, cat, today=TODAY)


def test_urgency_decreases_with_more_days_left():
    assert u(0) > u(3) > u(6) > u(15)


def test_expired_and_far_products():
    assert u(-2) == 1.0
    assert u(60) < 0.1


def test_opened_is_more_urgent_than_sealed():
    assert u(5, opened_ago=4) > u(5)


def test_categories_are_foodkeeper_based():
    assert set(CATEGORIES) == {
        "meat_fish", "dairy", "produce_soft", "produce_hard",
        "bakery", "prepared", "pantry",
    }


def test_categories_have_recommended_storage():
    assert {key: config.recommended_storage for key, config in CATEGORY_CONFIG.items()} == {
        "meat_fish": "fridge",
        "dairy": "fridge",
        "produce_soft": "fridge",
        "produce_hard": "pantry",
        "bakery": "pantry",
        "prepared": "fridge",
        "pantry": "pantry",
    }
    assert set(STORAGE_LOCATIONS) == {"fridge", "freezer", "pantry"}


def test_opened_meat_is_more_urgent_than_opened_pantry():
    chicken = u(30, opened_ago=2, cat="meat_fish")
    buckwheat = u(30, opened_ago=2, cat="pantry")
    assert chicken >= 0.9
    assert chicken > buckwheat


def test_opened_product_past_safe_term_is_urgent_despite_packaging_date():
    assert u(30, opened_ago=2, cat="meat_fish") == 1.0
    assert urgency_label(u(30, opened_ago=2, cat="meat_fish")) == "Терміново"


def test_demo_products_have_calibrated_urgency_zones():
    tomatoes = u(4, cat="produce_soft")
    eggs = u(6, cat="dairy")
    assert 0.35 <= tomatoes < 0.70
    assert 0.35 <= eggs < 0.70


def test_urgency_reasons_explain_main_cases():
    assert urgency_reason(TODAY - timedelta(days=1), None, "dairy", "fridge", TODAY) == "Прострочено"
    assert urgency_reason(TODAY + timedelta(days=30), None, "dairy", "pantry", TODAY) == "Зберігається поза холодильником"
    assert urgency_reason(TODAY + timedelta(days=30), TODAY - timedelta(days=3), "dairy", "fridge", TODAY) == "Відкрито 3 із 4 дн."
    assert urgency_reason(TODAY + timedelta(days=30), None, "dairy", "freezer", TODAY) == "У морозилці — запас тривалий"
    assert urgency_reason(TODAY + timedelta(days=20), None, "dairy", "fridge", TODAY) == "Термін достатній"


def test_freezer_slows_urgency():
    frozen_chicken = urgency(
        TODAY + timedelta(days=30),
        TODAY - timedelta(days=2),
        "meat_fish",
        today=TODAY,
        storage_location="freezer",
    )
    refrigerated_chicken = urgency(
        TODAY + timedelta(days=30),
        TODAY - timedelta(days=2),
        "meat_fish",
        today=TODAY,
        storage_location="fridge",
    )
    assert frozen_chicken < 0.35
    assert frozen_chicken < refrigerated_chicken


def test_perishable_product_in_pantry_is_critical():
    milk = urgency(
        TODAY + timedelta(days=30),
        TODAY,
        "dairy",
        today=TODAY,
        storage_location="pantry",
    )
    assert milk == 1.0


def test_labels():
    assert urgency_label(0.9) == "Терміново"
    assert urgency_label(0.5) == "Скоро"
    assert urgency_label(0.1) == "Є час"


def test_planner_uses_urgent_products_first():
    stock = {
        "яйця": (6, "шт", 0.9), "молоко": (500, "мл", 0.9),
        "картопля": (10, "шт", 0.05), "курка": (500, "г", 0.05), "сметана": (100, "г", 0.05),
    }
    plans, _ = plan_week(RECIPES, stock, days=1)
    breakfast = plans[0].slots[0]
    assert breakfast.meal_type == "breakfast"
    assert breakfast.recipe in {"Омлет з молоком", "Млинці"}
    assert "яйця" in breakfast.priority_ingredients


def test_planner_builds_shopping_list_and_does_not_overspend_stock():
    stock = {"яйця": (3, "шт", 0.9), "молоко": (100, "мл", 0.9)}
    plans, shopping = plan_week(RECIPES, stock, days=7)
    assert len(plans) == 7
    assert sum(len(day.slots) for day in plans) == 21
    assert shopping


def test_planner_creates_three_meal_slots_matching_recipe_types():
    recipes_by_name = {recipe["name"]: recipe for recipe in RECIPES}
    plans, _ = plan_week(RECIPES, {}, days=7)

    assert len(plans) == 7
    for day in plans:
        assert [slot.meal_type for slot in day.slots] == ["breakfast", "lunch", "dinner"]
        for slot in day.slots:
            assert slot.meal_type in recipes_by_name[slot.recipe]["meal_types"]


def test_batch_cooking_uses_leftover_on_next_day_without_rescanning_stock():
    recipes = [
        {"name": "Тестовий сніданок", "meal_types": ["breakfast"], "servings": 1, "keeps_days": 1, "ingredients": {}},
        {"name": "Тестовий борщ", "meal_types": ["lunch"], "servings": 2, "keeps_days": 3, "ingredients": {"капуста": (2, "г")}},
        {"name": "Тестова вечеря", "meal_types": ["dinner"], "servings": 1, "keeps_days": 1, "ingredients": {}},
    ]
    stock = {"капуста": (2, "г", 0.9)}

    plans, shopping = plan_week(recipes, stock, days=2)

    first_lunch, second_lunch = plans[0].slots[1], plans[1].slots[1]
    assert first_lunch.recipe == second_lunch.recipe == "Тестовий борщ"
    assert first_lunch.is_leftover is False
    assert second_lunch.is_leftover is True
    assert shopping == {}
