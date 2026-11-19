"""Базовий жадібний планувальник тижня з batch cooking."""
from dataclasses import dataclass, field

MISSING_PENALTY = 0.4
REPEAT_PENALTY = 0.5
RESCUE_THRESHOLD = 0.35
MEAL_TYPES = ("breakfast", "lunch", "dinner")


@dataclass
class MealSlot:
    meal_type: str
    recipe: str
    is_leftover: bool = False
    ingredients: dict = field(default_factory=dict)
    servings: int = 1
    portion_number: int = 1
    portion_weight_g: int = 0
    total_weight_g: int = 0
    priority_ingredients: list = field(default_factory=list)
    to_buy: dict = field(default_factory=dict)


@dataclass
class DayPlan:
    slots: list[MealSlot] = field(default_factory=list)


@dataclass
class _PreparedBatch:
    recipe: dict
    portions: int
    available_from: int
    expires_on: int
    next_portion_number: int = 2


def _score(recipe, stock, times_used):
    gain = missing = 0
    for name, (need, unit) in recipe["ingredients"].items():
        have, have_unit, urgency = stock.get(name, [0, unit, 0.0])
        if have_unit == unit and have >= need:
            gain += urgency
        else:
            missing += 1
    return gain - MISSING_PENALTY * missing - REPEAT_PENALTY * times_used.get(recipe["name"], 0)


def _find_leftover(leftovers, meal_type, day_index, used_today):
    for leftover in leftovers:
        if (
            leftover.portions > 0
            and leftover.available_from <= day_index <= leftover.expires_on
            and meal_type in leftover.recipe["meal_types"]
            and leftover.recipe["name"] not in used_today
        ):
            return leftover
    return None


def _consume_recipe(recipe, stock, shopping, priority_ingredients):
    to_buy = {}
    for name, (need, unit) in recipe["ingredients"].items():
        have, have_unit, urgency = stock.get(name, [0, unit, 0.0])
        if have_unit != unit:
            have = 0
        if have >= need:
            if urgency >= RESCUE_THRESHOLD:
                priority_ingredients.append(name)
            stock[name][0] = have - need
        else:
            short = need - have
            to_buy[name] = (short, unit)
            shopping[name] = (shopping.get(name, (0, unit))[0] + short, unit)
            if name in stock and have_unit == unit:
                stock[name][0] = 0
    return to_buy


def plan_week(recipes, stock, days=7):
    """Повертає 7-денний план із трьома слотами та список покупок."""
    stock = {name: list(values) for name, values in stock.items()}
    times_used, plans, shopping, leftovers = {}, [], {}, []

    for day_index in range(days):
        day_plan = DayPlan()
        used_today = set()
        for meal_type in MEAL_TYPES:
            leftover = _find_leftover(leftovers, meal_type, day_index, used_today)
            if leftover:
                leftover.portions -= 1
                used_today.add(leftover.recipe["name"])
                day_plan.slots.append(MealSlot(
                    meal_type=meal_type,
                    recipe=leftover.recipe["name"],
                    is_leftover=True,
                    servings=leftover.recipe["servings"],
                    portion_number=leftover.next_portion_number,
                    portion_weight_g=leftover.recipe.get("portion_weight_g", 0),
                    total_weight_g=leftover.recipe["servings"] * leftover.recipe.get("portion_weight_g", 0),
                ))
                leftover.next_portion_number += 1
                continue

            candidates = [
                recipe for recipe in recipes
                if meal_type in recipe["meal_types"] and recipe["name"] not in used_today
            ]
            if not candidates:
                candidates = [recipe for recipe in recipes if meal_type in recipe["meal_types"]]
            best = max(candidates, key=lambda recipe: _score(recipe, stock, times_used))
            times_used[best["name"]] = times_used.get(best["name"], 0) + 1
            used_today.add(best["name"])
            priority_ingredients = []
            to_buy = _consume_recipe(best, stock, shopping, priority_ingredients)
            day_plan.slots.append(MealSlot(
                meal_type=meal_type,
                recipe=best["name"],
                ingredients=dict(best["ingredients"]),
                servings=best["servings"],
                portion_number=1,
                portion_weight_g=best.get("portion_weight_g", 0),
                total_weight_g=best["servings"] * best.get("portion_weight_g", 0),
                priority_ingredients=priority_ingredients,
                to_buy=to_buy,
            ))

            leftover_portions = best["servings"] - 1
            if leftover_portions > 0:
                leftovers.append(_PreparedBatch(
                    recipe=best,
                    portions=leftover_portions,
                    available_from=day_index + 1,
                    expires_on=day_index + best["keeps_days"],
                ))
        plans.append(day_plan)
    return plans, shopping
