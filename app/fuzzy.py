"""Нечітка оцінка терміновості використання продукту.

Система типу Сугено нульового порядку: входи фазифікуються функціями належності,
правила «якщо-то» спрацьовують з силою min(...), вихід дефазифікується зваженим
середнім. Результат: від 0 (є час) до 1 (терміново).
"""
from datetime import date

# Швидкопсувні продукти «спливають» раніше, ніж свідчить дата на упаковці.
PERISHABILITY = {"fast": 0.6, "medium": 1.0, "slow": 1.6}
CATEGORIES = {
    "fast": "Швидкопсувні (молочні, м'ясо, гриби)",
    "medium": "Середні (овочі, фрукти, хліб)",
    "slow": "Тривалого зберігання (крупи, борошно)",
}


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
]


def _day_terms(e):
    return {"critical": _down(e, 1, 3), "soon": _tri(e, 1, 4, 8), "plenty": _up(e, 4, 9)}


def _open_terms(days_open):
    if days_open is None:
        return {"not_opened": 1.0, "recent": 0.0, "long": 0.0}
    return {"not_opened": 0.0, "recent": _down(days_open, 1, 4), "long": _up(days_open, 2, 6)}


def urgency(expires_on, opened_on=None, category="medium", today=None):
    today = today or date.today()
    effective = (expires_on - today).days * PERISHABILITY.get(category, 1.0)
    days_open = (today - opened_on).days if opened_on else None
    d, o = _day_terms(effective), _open_terms(days_open)

    num = den = 0.0
    for day_term, open_term, out in RULES:
        strength = d[day_term] if open_term is None else min(d[day_term], o[open_term])
        num += strength * out
        den += strength
    return round(num / den, 3) if den else 0.0


def urgency_label(u):
    if u >= 0.7:
        return "Терміново"
    if u >= 0.35:
        return "Скоро"
    return "Є час"
