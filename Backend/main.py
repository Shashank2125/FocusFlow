from fastapi import FastAPI
from app.db.database import engine
from app.models.user import User, Base
from app.models.mission import Mission
from app.db.database import SessionLocal
from datetime import date,timedelta,datetime
from pydantic import BaseModel
app=FastAPI()


class MissionUpdate(BaseModel):
    missionID:int
    date:str
    status:str
def calculate_xp(streak:int)->int:
    base=50
    bonus=min(streak*10,200)
    return base+bonus
def calculate_rank(xp:int)->str:
    if xp>=6000:
        return "A"
    elif xp>=3000:
        return "B"
    elif xp>=1500:
        return "C"
    elif xp>=500:
        return "D"
    return "E"
#rank multiplier
def rank_multiplier(rank:str)->float:
    return{
        "E":1.0,
        "D":1.1,
        "C":1.25,
        "B":1.5,
        "A":2   
    }.get(rank,1.0)
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
def complete_mission(mission_id:int):
    db=SessionLocal()
    today=date.today()
    #fetch mission
    mission=db.query(Mission).filter(Mission.id==mission_id).first()
    if not mission:
        db.close()
        return{"error": "Mission not found"}
    if mission.completed:
        db.close()
        return{"error": "Mission already completed"}
    #mark mission completed
    mission.completed=True
    #fetch user
    user=db.query(User).filter(User.id==mission.user_id).first()
    if not user:
        db.close()
        return {"error":"User not found"}
    #streak logic
    if user.last_active:
        last_day=user.last_active.date()
        if last_day==today-timedelta(days=1):
            user.streak+=1
        else:
            user.streak=1
    else:
        user.streak=1
    #xp increase according to the rank using multiplier
    base_xp=calculate_xp(user.streak)
    multiplier=rank_multiplier(user.rank)
    xp_gained=int(base_xp*multiplier)
    user.xp+=xp_gained
    #rank update
    new_rank=calculate_rank(user.xp)
    rank_changed=new_rank!=user.rank
    user.rank=new_rank
    #update last_active
    user.last_active=datetime.utcnow()
    #persist
    mission_id_value=mission.id# cache before closing db session
    db.commit()
    db.refresh(user)

    db.close()
    return {"status": "Mission completed", "mission_id":mission_id_value,"xp_gained":xp_gained,"base_xp":base_xp,"multiplier":multiplier,"total_xp":user.xp,"streak":user.streak,"rank":user.rank,"rank_changed":rank_changed}
@app.get("/users/daily-check/{user_id}")
def daily_check(user_id:int):
    db=SessionLocal()
    today=date.today()
    user=db.query(User).filter(User.id==user_id).first()
    if not user:
        db.close()
        return{"error":"User not found"}
    penalty_applied=False
    if user.last_active:
        day_missed=(today-user.last_active.date()).days
        if day_missed>1:
            user.streak=0
            user.xp=max(user.xp-100,0)
            penalty_applied=True
            db.commit()
    #cache value before commit
    xp_value=user.xp
    streak_value=user.streak
    db.close()
    return{
        "penalty":penalty_applied,
        "xp":xp_value,
        "streak":streak_value
    }
