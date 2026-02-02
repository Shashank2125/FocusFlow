# services/xp_service.py

def calculate_base_xp(streak: int) -> int:
    """
    Compute the base experience points for a given streak.
    
    Parameters:
        streak (int): Number of consecutive successful actions contributing to the bonus.
    
    Returns:
        int: Total base XP equal to 50 plus a streak bonus (10 per streak, capped at 200).
    """
    base = 50
    bonus = min(streak * 10, 200)
    return base + bonus


def rank_multiplier(rank: str) -> float:
    """
    Map a rank label to its numeric XP multiplier.
    
    Parameters:
        rank (str): Rank label expected to be one of "E", "D", "C", "B", or "A". Other values are treated as unrecognized.
    
    Returns:
        float: Multiplier corresponding to the given rank; `1.0` if the rank is unrecognized.
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
    Get the numeric multiplier for a difficulty label.
    
    Parameters:
        difficulty (str): Difficulty label expected to be "EASY", "NORMAL", or "HARD". If the label is unrecognized, the function uses the default multiplier.
    
    Returns:
        float: Multiplier for the difficulty — 1.0 for "EASY", 1.25 for "NORMAL", 1.5 for "HARD"; 1.0 if the input is unrecognized.
    """
    return {
        "EASY": 1.0,
        "NORMAL": 1.25,
        "HARD": 1.5
    }.get(difficulty, 1.0)


def calculate_rank(xp: int) -> str:
    """
    Determine a rank label based on total experience points (XP).
    
    Parameters:
        xp (int): Total accumulated experience points used to determine the rank.
    
    Returns:
        str: One of "A", "B", "C", "D", or "E" according to thresholds:
             "A" for xp >= 6000, "B" for xp >= 3000, "C" for xp >= 1500,
             "D" for xp >= 500, otherwise "E".
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
    Normalize a difficulty input to a canonical difficulty string.
    
    Parameters:
        difficulty: None, a string, or an object with a `value` attribute (e.g., an enum).
    
    Returns:
        difficulty_str (str): "NORMAL" if `difficulty` is None; if `difficulty` has a `value` attribute returns that attribute; otherwise returns `difficulty` as-is.
    """
    if difficulty is None:
        return "NORMAL"
    if hasattr(difficulty, "value"):
        return difficulty.value
    return difficulty


def calculate_xp(streak: int, rank: str, difficulty) -> dict:
    """
    Calculate the experience points (XP) gained for a single event based on streak, rank, and difficulty.
    
    Parameters:
        streak (int): Consecutive successful events count used to compute base XP bonus.
        rank (str): Rank label influencing the XP multiplier (e.g., "A", "B", "C", "D", "E").
        difficulty: Difficulty value, enum-like object, or string; if None, treated as "NORMAL".
    
    Returns:
        dict: A dictionary containing:
            xp_gained (int): Final XP awarded after applying rank and difficulty multipliers.
            base_xp (int): Base XP computed from the streak (includes streak bonus).
            rank_multiplier (float): Multiplier applied based on the provided rank.
            difficulty (str): Normalized difficulty label used for calculation.
            difficulty_multiplier (float): Multiplier applied based on the normalized difficulty.
    """
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