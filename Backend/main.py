from fastapi import FastAPI
from datetime import date, timedelta, datetime
from pydantic import BaseModel

from app.db.database import engine, SessionLocal
from app.models.user import User, Base
from app.models.mission import Mission
from services.xp_service import rank_progress
from services.xp_service import rank_up_reward,daily_xp_cap


from services.xp_service import (
    calculate_xp,
    calculate_rank,
    is_difficulty_allowed
)
from services.penalty_service import (
    rank_penalty,
    should_apply_penalty
)

app = FastAPI()


class MissionUpdate(BaseModel):
    missionID: int
    date: str
    status: str


Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "System Online"}


@app.post("/users/{username}")
def create_user(username: str):
    db = SessionLocal()
    user = User(username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return {"id": user.id, "username": user.username}


@app.post("/missions/today/{user_id}")
def get_or_create_today_mission(user_id: int):
    db = SessionLocal()
    today = date.today()

    mission = db.query(Mission).filter(
        Mission.user_id == user_id,
        Mission.mission_date == today
    ).first()

    if mission:
        db.close()
        return mission

    mission = Mission(
        user_id=user_id,
        title="Complete your daily focus session"
    )
    db.add(mission)
    db.commit()
    db.refresh(mission)
    db.close()
    return mission


@app.post("/missions/complete/{mission_id}")
def complete_mission(mission_id: int):
    db = SessionLocal()
    today = date.today()

    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        db.close()
        return {"error": "Mission not found"}

    if mission.completed:
        db.close()
        return {"error": "Mission already completed"}

    user = db.query(User).filter(User.id == mission.user_id).first()
    if not user:
        db.close()
        return {"error": "User not found"}

    difficulty_value = (
        mission.difficulty.value
        if hasattr(mission.difficulty, "value")
        else mission.difficulty
    )

    if not is_difficulty_allowed(user.rank, difficulty_value):
        db.close()
        return {
            "error": "Difficulty locked",
            "current_rank": user.rank,
            "difficulty": difficulty_value
        }

    # ✅ Complete mission
    mission.completed = True

    # ✅ Streak logic
    if user.last_active and user.last_active.date() == today - timedelta(days=1):
        user.streak += 1
    else:
        user.streak = 1

    # ✅ XP calculation
    xp_result = calculate_xp(
        streak=user.streak,
        rank=user.rank,
        difficulty=mission.difficulty
    )
    #infinite xp gain removal with introduction to CAP
    cap=daily_xp_cap(user.rank)
    #reset daily XP if new day
    if user.last_xp_date!=today:
        user.daily_xp=0
        user.last_xp_date=today
    available_xp=max(cap-user.daily_xp,0)
    xp_awarded=min(xp_result["xp_gained"],available_xp)
    user.xp+=xp_awarded
    user.daily_xp+=xp_awarded

    # ✅ Rank evaluation (Day 14)
    old_rank = user.rank
    new_rank = calculate_rank(user.xp)

    rank_changed = new_rank != old_rank
    rank_up = (
        rank_changed and
        ["E", "D", "C", "B", "A"].index(new_rank) >
        ["E", "D", "C", "B", "A"].index(old_rank)
    )

    user.rank = new_rank
    user.last_active = datetime.utcnow()
    reward = {"bonus_xp": 0, "unlock": None}

    bonus_xp = 0
    reward = {"bonus_xp": 0, "unlock": None}

    if rank_up:
        reward = rank_up_reward(new_rank)
        bonus_xp = reward["bonus_xp"]
        user.xp += bonus_xp



    db.commit()
    db.refresh(user)
    db.close()

    return {
        "status": "Mission completed",
        "mission_id": mission_id,
        **xp_result,
        "total_xp": user.xp,
        "streak": user.streak,
        "rank": user.rank,
        "rank_changed": rank_changed,
        "rank_up": rank_up,
        "rank_reward":reward,
        "daily_xp":user.daily_xp,
        "daily_xp_cap":cap,
        "xp_blocked":xp_result["xp_gained"]-xp_awarded
    } 



@app.get("/users/daily-check/{user_id}")
def daily_check(user_id: int):
    db = SessionLocal()
    today = date.today()

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        db.close()
        return {"error": "User not found"}

    penalty_applied = False
    penalty_xp = 0
    rank_dropped = False
    old_rank = user.rank

    if should_apply_penalty(user.last_active, today):
        penalty_xp = rank_penalty(user.rank)
        user.xp = max(user.xp - penalty_xp, 0)
        user.streak = 0
        penalty_applied = True

        # 🔽 Rank recalculation after penalty
        new_rank = calculate_rank(user.xp)
        if new_rank != old_rank:
            rank_dropped = True
            user.rank = new_rank

        user.last_active = datetime.utcnow()
        db.commit()

    result = {
        "penalty": penalty_applied,
        "penalty_xp": penalty_xp,
        "xp": user.xp,
        "streak": user.streak,
        "rank": user.rank,
        "rank_dropped": rank_dropped
    }

    db.close()
    return result

@app.get("/profile/{user_id}")
def get_profile(user_id: int):
    db = SessionLocal()

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        db.close()
        return {"error": "User not found"}

    profile = {
        "id": user.id,
        "username": user.username,
        "xp": user.xp,
        "rank": user.rank,
        "streak": user.streak,
        "last_active": user.last_active,
        "rank_progress": rank_progress(user.xp, user.rank)
    }

    db.close()
    return profile

