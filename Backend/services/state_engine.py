def determine_user_state(user, today):

    if user.xp_debt > 0:
        return "Recovery Mode"

    if user.overdrive_active and user.overdrive_expires == today:
        return "Overdrive Mode"

    if user.streak >= 15:
        return "Discipline Mode"

    if user.streak >= 8:
        return "Flow State"

    if user.streak >= 4:
        return "Momentum"

    return "Ignition"