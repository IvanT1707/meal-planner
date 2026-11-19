from datetime import date, timedelta

from app.domain.fuzzy import CATEGORIES, urgency, urgency_label
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


def test_opened_meat_is_more_urgent_than_opened_pantry():
    chicken = u(30, opened_ago=2, cat="meat_fish")
    buckwheat = u(30, opened_ago=2, cat="pantry")
    assert chicken >= 0.9
    assert chicken > buckwheat


def test_opened_product_past_safe_term_is_urgent_despite_packaging_date():
    assert u(30, opened_ago=2, cat="meat_fish") == 1.0
    assert urgency_label(u(30, opened_ago=2, cat="meat_fish")) == "Терміново"


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
    assert plans[0].recipe in {"Омлет з молоком", "Млинці"}
    assert "яйця" in plans[0].rescued


def test_planner_builds_shopping_list_and_does_not_overspend_stock():
    stock = {"яйця": (3, "шт", 0.9), "молоко": (100, "мл", 0.9)}
    plans, shopping = plan_week(RECIPES, stock, days=7)
    assert len(plans) == 7
    used_eggs = sum(1 for d in plans if "яйця" in d.rescued)
    assert used_eggs <= 1  # 3 яйця вистачає лише на один омлет
    assert shopping
