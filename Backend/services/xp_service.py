# services/xp_service.py
from services.game_engine import overdrive_multiplier

def calculate_base_xp(streak: int) -> int:
    """
    Compute base XP from streak.
    Base = 50
    Bonus = streak * 10 (capped at 200)
    """
    base = 50
    bonus = min(streak * 10, 200)
    return base + bonus


def rank_multiplier(rank: str) -> float:
    """
    Rank-based XP multiplier.
    """
    return {
        "E": 1.0,
        "D": 1.1,
        "C": 1.25,
        "B": 1.5,
        "A": 2.0
    }.get(rank, 1.0)


def difficulty_multiplier(difficulty: str) -> float:
    """
    Difficulty-based XP multiplier.
    """
    return {
        "EASY": 1.0,
        "NORMAL": 1.25,
        "HARD": 1.5
    }.get(difficulty, 1.0)


def calculate_rank(xp: int) -> str:
    """
    Determine rank from total XP.
    """
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
    """
    Normalize difficulty enum / string / None.
    """
    if difficulty is None:
        return "NORMAL"
    if hasattr(difficulty, "value"):
        return difficulty.value
    return difficulty
    



def calculate_xp(streak: int, rank: str, difficulty) -> dict:
    """
    Single source of truth for XP calculation.
    """
    

    base_xp = calculate_base_xp(streak)
    r_mult = rank_multiplier(rank)
    d_value = normalize_difficulty(difficulty)
    d_mult = difficulty_multiplier(d_value)

    #streak multiplier
    phase_data=streak_phase(streak)
    phase_mult=phase_data["multiplier"]

    xp_gained = int(base_xp * r_mult * d_mult*phase_mult*overdrive_multiplier)
    return {
        "xp_gained": xp_gained,
        "base_xp": base_xp,
        "rank_multiplier": r_mult,
        "difficulty": d_value,
        "difficulty_multiplier": d_mult
    }


def is_difficulty_allowed(rank: str, difficulty: str) -> bool:
    """
    Enforce difficulty locks by rank.
    """
    rank_limits = {
        "E": ["EASY", "NORMAL"],
        "D": ["EASY", "NORMAL"],
        "C": ["EASY", "NORMAL", "HARD"],
        "B": ["EASY", "NORMAL", "HARD"],
        "A": ["EASY", "NORMAL", "HARD"],
    }

    allowed = rank_limits.get(rank, ["EASY"])
    return difficulty in allowed
def rank_threshold(rank:str)->int:
    return{
        "E":500,
        "D":1500,
        "C":3000,
        "B":6000,
        "A":None#max rank
    }.get(rank)

def rank_up_reward(new_rank: str) -> dict:
    rewards = {
        "D": {"bonus_xp": 100, "unlock": "NORMAL"},
        "C": {"bonus_xp": 200, "unlock": "HARD"},
        "B": {"bonus_xp": 400, "unlock": "HARD"},
        "A": {"bonus_xp": 800, "unlock": "ELITE"}
    }
    return rewards.get(new_rank, {"bonus_xp": 0, "unlock": None})
def daily_xp_cap(rank:str)->int:
    return{
        "E":300,
        "D":400,
        "C":600,
        "B":800,
        "A":1000
    }.get(rank, 300)
RANK_THRESHOLDS = {
    "E": 0,
    "D": 500,
    "C": 1500,
    "B": 3000,
    "A": 6000
}

RANK_ORDER = ["E", "D", "C", "B", "A"]


def rank_progress(xp: int, rank: str) -> dict:
    if rank == "A":
        return {
            "progress": 100,
            "xp_remaining": 0,
            "next_rank": None
        }

    current_index = RANK_ORDER.index(rank)
    next_rank = RANK_ORDER[current_index + 1]

    base = RANK_THRESHOLDS[rank]
    next_threshold = RANK_THRESHOLDS[next_rank]

    total = next_threshold - base
    gained = xp - base

    progress = int((gained / total) * 100) if total > 0 else 0

    return {
        "progress": min(max(progress, 0), 100),
        "xp_remaining": max(next_threshold - xp, 0),
        "next_rank": next_rank
    }
def streak_phase(streak: int) -> dict:
    if streak >= 15:
        return {"phase": "Discipline Mode", "multiplier": 1.3}
    elif streak >= 8:
        return {"phase": "Flow State", "multiplier": 1.2}
    elif streak >= 4:
        return {"phase": "Momentum", "multiplier": 1.1}
    return {"phase": "Ignition", "multiplier": 1.0}





