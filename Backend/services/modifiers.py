# services/modifiers.py

def overdrive_multiplier(user) -> float:
    """
    Returns overdrive multiplier.
    Activated when XP debt becomes zero.
    """

    if hasattr(user, "xp_debt") and user.xp_debt == 0:
        return 1.5  # Example boost
    return 1.0