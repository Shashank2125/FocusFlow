from fastapi import FastAPI
from datetime import date, timedelta, datetime
from pydantic import BaseModel

from app.db.database import engine, SessionLocal
from app.models.user import User, Base
from app.models.mission import Mission

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

    mission.completed = True

    if user.last_active and user.last_active.date() == today - timedelta(days=1):
        user.streak += 1
    else:
        user.streak = 1

    xp_result = calculate_xp(
        streak=user.streak,
        rank=user.rank,
        difficulty=mission.difficulty
    )

    user.xp += xp_result["xp_gained"]

    new_rank = calculate_rank(user.xp)
    rank_changed = new_rank != user.rank
    user.rank = new_rank

    user.last_active = datetime.utcnow()

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
        "rank_changed": rank_changed
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

    if should_apply_penalty(user.last_active, today):
        penalty_xp = rank_penalty(user.rank)
        user.xp = max(user.xp - penalty_xp, 0)
        user.streak = 0
        user.last_active = datetime.utcnow()
        penalty_applied = True
        db.commit()

    result = {
        "penalty": penalty_applied,
        "penalty_xp": penalty_xp,
        "xp": user.xp,
        "streak": user.streak,
        "rank": user.rank
    }

    db.close()
    return result
