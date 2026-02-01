# services/penalty_service.py

from datetime import date


def rank_penalty(rank: str) -> int:
    return {
        "E": 100,
        "D": 150,
        "C": 250,
        "B": 400,
        "A": 600
    }.get(rank, 100)


def should_apply_penalty(last_active, today: date) -> bool:
    if not last_active:
        return False
    missed_days = (today - last_active.date()).days
    return missed_days > 1
