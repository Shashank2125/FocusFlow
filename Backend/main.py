from fastapi import FastAPI
from datetime import date, timedelta, datetime
from pydantic import BaseModel

from app.db.database import engine, SessionLocal
from app.models.user import User, Base
from app.models.mission import Mission
from services.xp_service import rank_progress
from services.xp_service import rank_up_reward,daily_xp_cap
from services.game_engine import process_mission_completion
from services.state_engine import determine_user_state

from services.penalty_service import apply_decay_penalty


from services.xp_service import (
    calculate_xp,
    calculate_rank,
    is_difficulty_allowed
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

    result = process_mission_completion(user, mission)

  


    db.commit()
    db.refresh(user)
    db.close()

    return {
        "status": "Mission completed",
        "mission_id": mission_id,
        **result["xp_result"],
        "total_xp": user.xp,
        "streak": user.streak,
        "rank": user.rank,
        "rank_changed": result["rank_changed"],
        "rank_up": result["rank_up"],
        "rank_reward":result["rank_reward"],
        "daily_xp":user.daily_xp,
        "daily_xp_cap":result["cap"],
        "xp_blocked":result["xp_result"]["xp_gained"]-result["xp_awarded"]
    } 




@app.get("/users/daily-check/{user_id}")
def daily_check(user_id: int):
    db = SessionLocal()
    today = date.today()

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        db.close()
        return {"error": "User not found"}

    result = apply_decay_penalty(user, today)

    if result["penalty"]:
        db.commit()

    db.refresh(user)
    if user.overdrive_expires != today:
        user.overdrive_active = False


    response = {
        "penalty": result["penalty"],
        "penalty_xp": result["penalty_xp"],
        "xp": user.xp,
        "xp_debt": user.xp_debt,  # if you added debt
        "streak": user.streak,
        "rank": user.rank,
        "rank_dropped": result["rank_dropped"],
        "momentum_shield_active": result["momentum_shield_active"]
    }

    db.close()
    return response



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
@app.get("/dashboard/{user_id}")
def dashboard(user_id: int):
    db = SessionLocal()
    today = date.today()

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        db.close()
        return {"error": "User not found"}
    

    state = determine_user_state(user, today)

    cap = daily_xp_cap(user.rank)
    remaining = max(cap - user.daily_xp, 0)

    data = {
        "xp": user.xp,
        "rank": user.rank,
        "streak": user.streak,
        "daily_xp": user.daily_xp,
        "daily_xp_cap": cap,
        "xp_remaining_today": remaining,
        "rank_progress": rank_progress(user.xp, user.rank),
        "can_gain_xp_today": remaining > 0,
        "current_state": state
    }

    db.close()
    return data


