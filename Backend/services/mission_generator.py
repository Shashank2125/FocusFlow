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

    # Recovery state
    if hasattr(user, "xp_debt") and user.xp_debt > 0:
        difficulty = "EASY"
        description = random.choice(RECOVERY_MISSIONS)

    # High streak users
    elif user.streak >= 15:
        difficulty = "HARD"
        description = random.choice(HARD_MISSIONS)

    # Medium streak
    elif user.streak >= 5:
        difficulty = "NORMAL"
        description = random.choice(NORMAL_MISSIONS)

    # Beginner
    else:
        difficulty = "EASY"
        description = random.choice(EASY_MISSIONS)
    log_event(user, "MISSION_GENERATED", {
    "difficulty": difficulty,
    "description": description
    })

    return {
        "description": description,
        "difficulty": difficulty
    }