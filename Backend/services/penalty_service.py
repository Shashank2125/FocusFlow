from datetime import datetime
from services.xp_service import calculate_rank


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
        return {
            "penalty": False,
            "penalty_xp": 0,
            "rank_dropped": False,
            "momentum_shield_active": False
        }

    days_missed = (today - user.last_active.date()).days

    # No penalty for 0 or 1 day gap
    if days_missed <= 1:
        return {
            "penalty": False,
            "penalty_xp": 0,
            "rank_dropped": False,
            "momentum_shield_active": False
        }

    base_penalty = rank_penalty(user.rank)
    momentum_shield = user.streak >= 15

    # Scaling decay (days_missed - 1 because first missed day is buffer)
    decay_penalty = base_penalty * (days_missed - 1)

    # Momentum shield blocks ONE day's penalty
    if momentum_shield:
        decay_penalty -= base_penalty

    decay_penalty = max(decay_penalty, 0)

    immediate_loss = decay_penalty // 2
    debt_loss = decay_penalty - immediate_loss

    user.xp = max(user.xp - immediate_loss, 0)
    user.xp_debt += debt_loss
    user.streak = 0


    old_rank = user.rank
    new_rank = calculate_rank(user.xp)

    rank_dropped = new_rank != old_rank
    user.rank = new_rank

    user.last_active = datetime.utcnow()

    return {
        "penalty": True,
        "penalty_xp": decay_penalty,
        "rank_dropped": rank_dropped,
        "momentum_shield_active": momentum_shield
    }
