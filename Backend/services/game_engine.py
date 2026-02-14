from datetime import datetime, date, timedelta
from services.xp_service import (
    calculate_xp,
    calculate_rank,
    daily_xp_cap,
    rank_up_reward,
    streak_phase
)

RANK_ORDER = ["E", "D", "C", "B", "A"]

def process_mission_completion(user, mission):
    today = date.today()

    # --- Streak Logic ---
    if user.last_active and user.last_active.date() == today - timedelta(days=1):
        user.streak += 1
    else:
        user.streak = 1

    # --- Phase Logic ---
    phase_data = streak_phase(user.streak)
    phase_multiplier = phase_data["multiplier"]

    # --- XP Calculation ---
    xp_result = calculate_xp(
        streak=user.streak,
        rank=user.rank,
        difficulty=mission.difficulty,
        phase_multiplier=phase_multiplier
    )

    cap = daily_xp_cap(user.rank)

    if user.last_xp_date != today:
        user.daily_xp = 0
        user.last_xp_date = today

    available_xp = max(cap - user.daily_xp, 0)
    xp_awarded = min(xp_result["xp_gained"], available_xp)

    user.xp += xp_awarded
    user.daily_xp += xp_awarded

    # --- Rank Evaluation ---
    old_rank = user.rank
    new_rank = calculate_rank(user.xp)

    old_index = RANK_ORDER.index(old_rank)
    new_index = RANK_ORDER.index(new_rank)

    rank_changed = new_rank != old_rank
    rank_up = new_index > old_index

    reward = {"bonus_xp": 0, "unlock": None}

    if rank_up:
        reward = rank_up_reward(new_rank)
        user.xp += reward["bonus_xp"]

    user.rank = new_rank
    user.last_active = datetime.utcnow()
    mission.completed = True

    return {
        "xp_result": xp_result,
        "xp_awarded": xp_awarded,
        "rank_changed": rank_changed,
        "rank_up": rank_up,
        "rank_reward": reward,
        "daily_cap": cap,
        "phase": phase_data["phase"]
    }
