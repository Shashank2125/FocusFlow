# services/mission_generator.py

import random
from services.telemetry_service import log_event


EASY_MISSIONS = [
    "Study for 20 minutes",
    "Read 10 pages",
    "Write 1 paragraph",
]

NORMAL_MISSIONS = [
    "Study for 45 minutes",
    "Solve 5 coding problems",
    "Read 25 pages",
]

HARD_MISSIONS = [
    "Deep work for 90 minutes",
    "Build a feature",
    "Solve 15 coding problems",
]

RECOVERY_MISSIONS = [
    "Complete 1 easy task",
    "Review yesterday's work",
    "Fix one pending task"
]


def generate_mission(user):

    state = getattr(user, "current_state", "NORMAL")

    # Behavior-state driven mission selection
    if state == "BURNOUT":
        difficulty = "EASY"
        description = random.choice(RECOVERY_MISSIONS)

    elif state == "RECOVERY":
        difficulty = "EASY"
        description = random.choice(EASY_MISSIONS)

    elif state == "MOMENTUM":
        difficulty = "NORMAL"
        description = random.choice(NORMAL_MISSIONS)

    elif state == "FLOW":
        difficulty = "HARD"
        description = random.choice(HARD_MISSIONS)

    elif state == "DISCIPLINE":
        difficulty = "HARD"
        description = random.choice(HARD_MISSIONS)

    else:
        difficulty = "EASY"
        description = random.choice(EASY_MISSIONS)

    # Telemetry event
    log_event(user, "MISSION_GENERATED", {
        "state": state,
        "difficulty": difficulty,
        "description": description
    })

    return {
        "description": description,
        "difficulty": difficulty
    }