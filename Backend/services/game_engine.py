# services/game_engine.py

from datetime import datetime
from services.xp_service import calculate_xp, calculate_rank


def process_mission(user, mission):

    xp_result = calculate_xp(
        streak=user.streak,
        rank=user.rank,
        difficulty=mission.difficulty,
        user=user
    )

    xp_awarded = xp_result["xp_gained"]

    user.xp += xp_awarded
    user.daily_xp += xp_awarded

    old_rank = user.rank
    new_rank = calculate_rank(user.xp)

    user.rank = new_rank
    user.last_active = datetime.utcnow()
    mission.completed = True

    return {
        "xp_result": xp_result,
        "rank_changed": new_rank != old_rank
    }