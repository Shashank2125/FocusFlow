# services/penalty_service.py

from datetime import date


def rank_penalty(rank: str) -> int:
    """
    Map a rank letter to its corresponding penalty score.
    
    Parameters:
        rank (str): Rank letter expected to be one of "A", "B", "C", "D", or "E".
    
    Returns:
        int: Penalty score: 600 for "A", 400 for "B", 250 for "C", 150 for "D", and 100 for "E" or any unrecognized rank.
    """
    return {
        "E": 100,
        "D": 150,
        "C": 250,
        "B": 400,
        "A": 600
    }.get(rank, 100)


def should_apply_penalty(last_active, today: date) -> bool:
    """
    Determine whether a penalty should be applied based on how many full days have passed since last activity.
    
    Parameters:
        last_active (datetime.datetime | Any): An object representing the last activity time; must implement a `.date()` method returning a datetime.date. If falsy (e.g., None), no penalty is applied.
        today (datetime.date): The current date used to compute elapsed days since `last_active.date()`.
    
    Returns:
        bool: `true` if more than one full day has passed since `last_active.date()`, `false` otherwise.
    """
    if not last_active:
        return False
    missed_days = (today - last_active.date()).days
    return missed_days > 1