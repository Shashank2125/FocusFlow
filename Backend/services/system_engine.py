# services/system_engine.py

from services.penalty_service import apply_decay_penalty
from services.game_engine import process_mission


def process_daily_cycle(user, mission, today):

    response = {}

    # 1️⃣ Apply decay
    penalty_result = apply_decay_penalty(user, today)
    response["penalty"] = penalty_result

    # 2️⃣ Process mission if exists and not completed
    if mission and not mission.completed:
        mission_result = process_mission(user, mission)
        response["mission"] = mission_result
    else:
        response["mission"] = None

    return response