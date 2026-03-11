# services/state_engine.py

def get_behavior_state(user):
    """
    Determines the user's behavioral state.
    """

    # Burnout
    if user.xp_debt > 300:
        return "BURNOUT"

    # Recovery
    if user.xp_debt > 0:
        return "RECOVERY"

    # Discipline
    if user.streak >= 20:
        return "DISCIPLINE"

    # Flow
    if user.streak >= 10:
        return "FLOW"

    # Momentum
    if user.streak >= 4:
        return "MOMENTUM"

    return "NORMAL"
from services.telemetry_service import log_event


def update_behavior_state(user):

    state = get_behavior_state(user)

    if user.current_state != state:

        log_event(user, "STATE_CHANGED", {
            "old_state": user.current_state,
            "new_state": state
        })

        user.current_state = state

    return state