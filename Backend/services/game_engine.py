# services/game_engine.py

from datetime import datetime
from services.xp_service import calculate_xp, calculate_rank
from services.telemetry_service import log_event


def process_mission(user, mission):

    xp_result = calculate_xp(
        streak=user.streak,
        rank=user.rank,
        difficulty=mission.difficulty,
        user=user
    )

    xp_awarded = xp_result["xp_gained"]

    # Update XP
    user.xp += xp_awarded
    user.daily_xp += xp_awarded

    old_rank = user.rank
    new_rank = calculate_rank(user.xp)

    # Update rank
    user.rank = new_rank

    # Log mission completion
    log_event(user, "MISSION_COMPLETED", {
        "xp_gained": xp_awarded,
        "new_total_xp": user.xp,
        "streak": user.streak,
        "rank": user.rank
    })

    # Log rank change separately
    if new_rank != old_rank:
        log_event(user, "RANK_CHANGED", {
            "old_rank": old_rank,
            "new_rank": new_rank
        })

    # Update activity
    user.last_active = datetime.utcnow()
    mission.completed = True

    return {
        "xp_result": xp_result,
        "rank_changed": new_rank != old_rank
    }