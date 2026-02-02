# services/xp_service.py

def calculate_base_xp(streak: int) -> int:
    base = 50
    bonus = min(streak * 10, 200)
    return base + bonus


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


def normalize_difficulty(difficulty):
    if difficulty is None:
        return "NORMAL"
    if hasattr(difficulty, "value"):
        return difficulty.value
    return difficulty


def calculate_xp(streak: int, rank: str, difficulty) -> dict:
    base_xp = calculate_base_xp(streak)
    r_mult = rank_multiplier(rank)
    d_value = normalize_difficulty(difficulty)
    d_mult = difficulty_multiplier(d_value)

    xp_gained = int(base_xp * r_mult * d_mult)

    return {
        "xp_gained": xp_gained,
        "base_xp": base_xp,
        "rank_multiplier": r_mult,
        "difficulty": d_value,
        "difficulty_multiplier": d_mult
    }
