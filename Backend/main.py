from fastapi import FastAPI
from app.db.database import engine
from app.models.user import User, Base
from app.models.mission import Mission
from app.db.database import SessionLocal
from datetime import date,timedelta,datetime
from pydantic import BaseModel
from services.xp_service import calculate_xp,calculate_rank
app=FastAPI()


class MissionUpdate(BaseModel):
    missionID:int
    date:str
    status:str





def rank_penalty(rank:str)->int:
    """
    Map a rank letter to its associated XP penalty.
    
    Parameters:
    	rank (str): Rank letter ('A' through 'E').
    
    Returns:
    	penalty_xp (int): Penalty XP for the given rank: A=600, B=400, C=250, D=150, E=100. Returns 100 if the rank is unrecognized.
    """
    return{
        "E":100,
        "D":150,
        "C":250,
        "B":400,
        "A":600
    }.get(rank,100)
#@app.post("/missions/update-status")
#def update_status(data:MissionUpdate):
    #print("MISSION UPDATE:", data)
    #return{"message":"status saved"}

Base.metadata.create_all(bind=engine)
@app.get("/")
def root():
    return {"status":"System Online"}
@app.post("/users/{username}")
def create_user(username: str):
    from app.db.database import SessionLocal
    db = SessionLocal()
    user = User(username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return {"id": user.id, "username": user.username}
@app.post("/missions/today/{user_id}")
def get_or_create_today_mission(user_id:int):
    """
    Retrieve the user's mission for today or create a new one if none exists.
    
    Parameters:
        user_id (int): The database ID of the user.
    
    Returns:
        Mission: The existing or newly created Mission for today's date.
    """
    db=SessionLocal()

    today=date.today()
    mission=db.query(Mission).filter(
        Mission.user_id==user_id,
        Mission.mission_date==today
    ).first()
    if mission:
        db.close()
        return mission
    mission=Mission(
        user_id=user_id,
        title="Complete your daily focus session"
    )
    db.add(mission)
    db.commit()
    db.refresh(mission)
    db.close()
    return mission
#business logic
@app.post("/missions/complete/{mission_id}")
def complete_mission(mission_id: int):
    """
    Complete a mission, apply XP and streak updates to the associated user, and persist changes to the database.
    
    On success, marks the mission as completed, updates the user's streak, increments the user's XP using the XP service, recalculates and updates the user's rank, sets the user's last_active timestamp to now, and commits these changes.
    
    Returns:
        dict: On error, a dictionary with an `"error"` message describing the failure (e.g., mission not found, mission already completed, or user not found).
        On success, a dictionary containing:
            - "status" (str): Confirmation message "Mission completed".
            - "mission_id" (int): ID of the completed mission.
            - ...fields returned by the XP service (merged from `xp_result`, e.g., `"xp_gained"` and any XP breakdown).
            - "total_xp" (int): User's XP after applying the gained XP.
            - "streak" (int): User's current streak after the update.
            - "rank" (str): User's updated rank after recalculation.
            - "rank_changed" (bool): `true` if the user's rank changed as a result of this completion, `false` otherwise.
    """
    db = SessionLocal()
    today = date.today()

    # Fetch mission
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        db.close()
        return {"error": "Mission not found"}
    if mission.completed:
        db.close()
        return {"error": "Mission already completed"}

    mission.completed = True

    # Fetch user
    user = db.query(User).filter(User.id == mission.user_id).first()
    if not user:
        db.close()
        return {"error": "User not found"}

    # Streak logic
    if user.last_active:
        last_day = user.last_active.date()
        if last_day == today - timedelta(days=1):
            user.streak += 1
        else:
            user.streak = 1
    else:
        user.streak = 1

    # XP SERVICE (single source of truth)
    xp_result = calculate_xp(
        streak=user.streak,
        rank=user.rank,
        difficulty=mission.difficulty
    )

    user.xp += xp_result["xp_gained"]

    # Rank update
    new_rank = calculate_rank(user.xp)
    rank_changed = new_rank != user.rank
    user.rank = new_rank

    # Update last active
    user.last_active = datetime.utcnow()

    # Cache before commit
    mission_id_value = mission.id

    db.commit()
    db.refresh(user)
    db.close()

    return {
        "status": "Mission completed",
        "mission_id": mission_id_value,
        **xp_result,
        "total_xp": user.xp,
        "streak": user.streak,
        "rank": user.rank,
        "rank_changed": rank_changed
    }
@app.get("/users/daily-check/{user_id}")
def daily_check(user_id:int):
    """
    Check a user's daily activity and apply a rank-based penalty when the user has missed more than one day.
    
    If the user has a recorded last_active date and the gap to today is greater than one day, this resets the user's streak to 0 and deducts XP using the rank_penalty mapping, never letting XP drop below 0. If the user does not exist, an error mapping is returned.
    
    Parameters:
        user_id (int): The database ID of the user to perform the daily check for.
    
    Returns:
        dict: On success, a mapping with:
            - "penalty" (bool): True if a penalty was applied, False otherwise.
            - "xp" (int): The user's current XP after any penalty.
            - "streak" (int): The user's current streak after any reset.
            - "penalty_xp" (int): The XP amount deducted due to the penalty (0 if none).
            - "rank" (str): The user's current rank string.
        dict: If the user is not found, returns {"error": "User not found"}.
    """
    db=SessionLocal()
    today=date.today()
    user=db.query(User).filter(User.id==user_id).first()
    if not user:
        db.close()
        return{"error":"User not found"}
    penalty_applied=False
    penalty_xp=0
    if user.last_active:
        day_missed=(today-user.last_active.date()).days
        #apply penalty based on user rank
        if day_missed>1:
            penalty_xp=rank_penalty(user.rank)
            user.streak=0
            user.xp=max(user.xp-penalty_xp,0)
            penalty_applied=True
            db.commit()
    #cache value before commit
    xp_value=user.xp
    streak_value=user.streak
    db.close()
    return{
        "penalty":penalty_applied,
        "xp":xp_value,
        "streak":streak_value,
        "penalty_xp":penalty_xp,
        "rank":user.rank
    }