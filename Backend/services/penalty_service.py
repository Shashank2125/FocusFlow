# services/xp_service.py

from services.modifiers import overdrive_multiplier

RANK_THRESHOLDS = {
    "E": 0,
    "D": 500,
    "C": 1500,
    "B": 3000,
    "A": 6000
}

RANK_ORDER = ["E", "D", "C", "B", "A"]


def calculate_base_xp(streak: int) -> int:
    return 50 + min(streak * 10, 200)


def rank_multiplier(rank: str) -> float:
    return {
        "E": 1.0,
        "D": 1.1,
        "C": 1.25,
        "B": 1.5,
        "A": 2.0
    }.get(rank, 1.0)


def difficulty_multiplier(difficulty: str) -> float:
    return {
        "EASY": 1.0,
        "NORMAL": 1.25,
        "HARD": 1.5
    }.get(difficulty, 1.0)


def calculate_rank(xp: int) -> str:
    if xp >= 6000:
        return "A"
    elif xp >= 3000:
        return "B"
    elif xp >= 1500:
        return "C"
    elif xp >= 500:
        return "D"
    return "E"


def streak_phase(streak: int):
    if streak >= 15:
        return {"phase": "Discipline Mode", "multiplier": 1.3}
    elif streak >= 8:
        return {"phase": "Flow State", "multiplier": 1.2}
    elif streak >= 4:
        return {"phase": "Momentum", "multiplier": 1.1}
    return {"phase": "Ignition", "multiplier": 1.0}


def calculate_xp(streak, rank, difficulty, user):
    base = calculate_base_xp(streak)
    r_mult = rank_multiplier(rank)
    d_mult = difficulty_multiplier(difficulty)

    phase_data = streak_phase(streak)
    phase_mult = phase_data["multiplier"]

    o_mult = overdrive_multiplier(user)

    xp = int(base * r_mult * d_mult * phase_mult * o_mult)

    return {
        "xp_gained": xp,
        "base_xp": base,
        "phase": phase_data["phase"],
        "phase_multiplier": phase_mult,
        "overdrive_multiplier": o_mult
    }