"""Базовий (жадібний) планувальник тижня."""
from dataclasses import dataclass, field

MISSING_PENALTY = 0.4
REPEAT_PENALTY = 0.5
RESCUE_THRESHOLD = 0.35


@dataclass
class DayPlan:
    recipe: str
    rescued: list = field(default_factory=list)
    to_buy: dict = field(default_factory=dict)


def _score(recipe, stock, times_used):
    gain = missing = 0
    for name, (need, unit) in recipe["ingredients"].items():
        have, have_unit, urg = stock.get(name, [0, unit, 0.0])
        if have_unit == unit and have >= need:
            gain += urg
        else:
            missing += 1
    return gain - MISSING_PENALTY * missing - REPEAT_PENALTY * times_used.get(recipe["name"], 0)


def plan_week(recipes, stock, days=7):
    """stock: {назва: (кількість, одиниця, терміновість)} -> (список DayPlan, список покупок)."""
    stock = {k: list(v) for k, v in stock.items()}
    times_used, plans, shopping = {}, [], {}

    for _ in range(days):
        best = max(recipes, key=lambda r: _score(r, stock, times_used))
        times_used[best["name"]] = times_used.get(best["name"], 0) + 1
        day = DayPlan(recipe=best["name"])

        for name, (need, unit) in best["ingredients"].items():
            have, have_unit, urg = stock.get(name, [0, unit, 0.0])
            if have_unit != unit:
                have = 0
            if have >= need:
                if urg >= RESCUE_THRESHOLD:
                    day.rescued.append(name)
                stock[name][0] = have - need
            else:
                short = need - have
                day.to_buy[name] = (short, unit)
                shopping[name] = (shopping.get(name, (0, unit))[0] + short, unit)
                if name in stock and have_unit == unit:
                    stock[name][0] = 0
        plans.append(day)
    return plans, shopping
