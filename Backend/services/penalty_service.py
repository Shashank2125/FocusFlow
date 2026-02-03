# services/penalty_service.py

from datetime import date, datetime
from typing import Optional


def rank_penalty(rank: str) -> int:
    """
    Map a rank letter to its corresponding XP penalty.
    """
    return {
        "E": 100,
        "D": 150,
        "C": 250,
        "B": 400,
        "A": 600
    }.get(rank, 100)


def should_apply_penalty(last_active: Optional[datetime], today: date) -> bool:
    """
    Apply penalty if more than one full day was missed.
    """
    if not last_active:
        return False

    missed_days = (today - last_active.date()).days
    return missed_days > 1
