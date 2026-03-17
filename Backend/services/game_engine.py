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

    xp_gained = xp_result["xp_gained"]

    # --- 💥 Debt Repayment Logic ---
    if getattr(user, "xp_debt", 0) > 0:

        repayment = xp_gained // 2
        actual_xp = xp_gained - repayment

        user.xp_debt = max(user.xp_debt - repayment, 0)
        user.xp += actual_xp

        debt_cleared = user.xp_debt == 0

    else:
        actual_xp = xp_gained
        repayment = 0
        debt_cleared = False
        user.xp += actual_xp

    user.daily_xp += actual_xp

    old_rank = user.rank
    new_rank = calculate_rank(user.xp)
    user.rank = new_rank

    # --- Telemetry ---
    log_event(user, "MISSION_COMPLETED", {
        "xp_gained": xp_gained,
        "actual_xp": actual_xp,
        "debt_repaid": repayment,
        "remaining_debt": user.xp_debt,
        "streak": user.streak,
        "rank": user.rank
    })

    if debt_cleared:
        log_event(user, "DEBT_CLEARED", {
            "user_id": user.id
        })

    if new_rank != old_rank:
        log_event(user, "RANK_CHANGED", {
            "old_rank": old_rank,
            "new_rank": new_rank
        })

    user.last_active = datetime.utcnow()
    mission.completed = True

    return {
        "xp_result": xp_result,
        "actual_xp": actual_xp,
        "debt_repaid": repayment,
        "rank_changed": new_rank != old_rank
    }