# services/penalty_service.py

from datetime import datetime
from services.xp_service import calculate_rank
from services.telemetry_service import log_event


def rank_penalty(rank: str) -> int:
    return {
        "E": 100,
        "D": 150,
        "C": 250,
        "B": 400,
        "A": 600
    }.get(rank, 100)


def apply_decay_penalty(user, today):

    if not user.last_active:
        return {"penalty": False}

    days_missed = (today - user.last_active.date()).days

    if days_missed <= 1:
        return {"penalty": False}

    momentum_shield = user.streak >= 15
    penalty_value = rank_penalty(user.rank)

    # Scaled decay
    decay = penalty_value * (days_missed - 1)

    if momentum_shield:
        decay -= penalty_value

    decay = max(decay, 0)

    # Debt split
    immediate_loss = decay // 2
    debt_loss = decay - immediate_loss

    user.xp = max(user.xp - immediate_loss, 0)
    user.xp_debt += debt_loss
    user.streak = 0

    old_rank = user.rank
    new_rank = calculate_rank(user.xp)

    if new_rank != old_rank:
        user.rank = new_rank

    user.last_active = datetime.utcnow()

    # ✅ Telemetry logging
    log_event(user, "PENALTY_APPLIED", {
        "days_missed": days_missed,
        "penalty_xp": decay,
        "immediate_loss": immediate_loss,
        "debt_added": debt_loss,
        "momentum_shield": momentum_shield
    })

    return {
        "penalty": True,
        "penalty_xp": decay,
        "momentum_shield_active": momentum_shield
    }