# services/penalty_service.py

from datetime import date, datetime
from typing import Optional
from services.xp_service import calculate_rank
# services/penalty_service.py

from datetime import datetime
from services.xp_service import calculate_rank
from services.penalty_service import rank_penalty


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





def apply_decay_penalty(user, today):

    if not user.last_active:
        return {
            "penalty": False,
            "penalty_xp": 0,
            "rank_dropped": False,
            "momentum_shield_active": False
        }

    days_missed = (today - user.last_active.date()).days

    if days_missed <= 1:
        return {
            "penalty": False,
            "penalty_xp": 0,
            "rank_dropped": False,
            "momentum_shield_active": False
        }

    momentum_shield = user.streak >= 15
    penalty_xp = rank_penalty(user.rank)

    user.xp = max(user.xp - penalty_xp, 0)
    user.streak = 0

    old_rank = user.rank
    new_rank = calculate_rank(user.xp)

    rank_dropped = False
    if new_rank != old_rank and not momentum_shield:
        user.rank = new_rank
        rank_dropped = True

    user.last_active = datetime.utcnow()

    return {
        "penalty": True,
        "penalty_xp": penalty_xp,
        "rank_dropped": rank_dropped,
        "momentum_shield_active": momentum_shield
    }


