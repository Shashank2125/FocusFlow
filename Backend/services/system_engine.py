# services/system_engine.py

from services.penalty_service import apply_decay_penalty
from services.state_engine import update_behavior_state
from services.mission_generator import generate_mission
from services.game_engine import process_mission


def process_daily_cycle(user, mission, today):

    response = {}

    # 1️⃣ Apply decay penalty
    penalty_result = apply_decay_penalty(user, today)
    response["penalty"] = penalty_result

    # 2️⃣ Update behavior state (after penalties)
    state_before = update_behavior_state(user)
    response["state_before"] = state_before

    # 3️⃣ Generate mission if none exists
    if mission is None:

        new_mission = generate_mission(user)

        response["generated_mission"] = new_mission
        response["mission_completed"] = False

    else:

        # 4️⃣ Process mission completion
        if not mission.completed:

            mission_result = process_mission(user, mission)
            response["mission"] = mission_result
            response["mission_completed"] = True

        else:

            response["mission_completed"] = False

    # 5️⃣ Recalculate behavior state after mission
    state_after = update_behavior_state(user)
    response["state_after"] = state_after

    # 6️⃣ Return updated user stats
    response["user_stats"] = {
        "xp": user.xp,
        "rank": user.rank,
        "streak": user.streak,
        "xp_debt": getattr(user, "xp_debt", 0),
        "state": user.current_state
    }

    return response