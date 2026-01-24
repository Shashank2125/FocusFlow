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
@app.post("/missions/update-status")
def update_status(data:MissionUpdate):
    print("MISSION UPDATE:", data)
    return{"message":"status saved"}

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
    #xp curve
    xp_gained=calculate_xp(user.streak)
    user.xp+=xp_gained
    #update last_active
    user.last_active=datetime.utcnow()
    #persist
    mission_id_value=mission.id# cache before closing db session
    db.commit()
    db.refresh(user)

    db.close()
    return {"status": "Mission completed","xp": user.xp, "mission_id":mission_id_value,"xp_gained":xp_gained,"total_xp":user.xp,"streak":user.streak}
