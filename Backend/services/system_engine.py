from services.mission_generator import generate_mission
from services.penalty_service import apply_decay_penalty
from services.game_engine import process_mission


def process_daily_cycle(user, mission, today):

    response = {}

    # Apply decay
    penalty_result = apply_decay_penalty(user, today)
    response["penalty"] = penalty_result

    # Generate mission if none exists
    if mission is None:
        new_mission = generate_mission(user)
        response["generated_mission"] = new_mission
        return response

    # Process mission completion
    if not mission.completed:
        mission_result = process_mission(user, mission)
        response["mission"] = mission_result

    return response