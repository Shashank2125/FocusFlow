def determine_user_state(user, today):

    # --- Debt state overrides everything ---
    if getattr(user, "xp_debt", 0) > 0:
        return "Recovery Mode"

    # --- Overdrive check ---
    if getattr(user, "overdrive_active", False):
        if user.overdrive_expires and user.overdrive_expires >= today:
            return "Overdrive Mode"

    # --- Streak based states ---
    if user.streak >= 15:
        return "Discipline Mode"

    if user.streak >= 8:
        return "Flow State"

    if user.streak >= 4:
        return "Momentum"

    return "Ignition"