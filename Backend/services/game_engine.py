from datetime import datetime, date
from services.xp_service import (
    calculate_xp,
    calculate_rank,
    daily_xp_cap,
    rank_up_reward
)

def process_mission_completion(user, mission):
    today = date.today()

    # Streak logic
    if user.last_active and user.last_active.date() == today.replace(day=today.day - 1):
        user.streak += 1
    else:
        user.streak = 1

    # XP calculation
    xp_result = calculate_xp(
        streak=user.streak,
        rank=user.rank,
        difficulty=mission.difficulty
    )

    cap = daily_xp_cap(user.rank)

    if user.last_xp_date != today:
        user.daily_xp = 0
        user.last_xp_date = today

    available_xp = max(cap - user.daily_xp, 0)
    xp_awarded = min(xp_result["xp_gained"], available_xp)

    user.xp += xp_awarded
    user.daily_xp += xp_awarded

    # Rank evaluation
    old_rank = user.rank
    new_rank = calculate_rank(user.xp)

    rank_changed = new_rank != old_rank
    rank_up = False
    reward = {"bonus_xp": 0, "unlock": None}

    if rank_changed:
        if new_rank != old_rank:
            reward = rank_up_reward(new_rank)
            user.xp += reward["bonus_xp"]
            rank_up = True

    user.rank = new_rank
    user.last_active = datetime.utcnow()
    mission.completed = True

    return {
        "xp_result": xp_result,
        "xp_awarded": xp_awarded,
        "rank_changed": rank_changed,
        "rank_up": rank_up,
        "rank_reward": reward,
        "daily_cap": cap
    }
