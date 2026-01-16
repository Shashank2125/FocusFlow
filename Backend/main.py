from fastapi import FastAPI
from app.db.database import engine
from app.models.user import User, Base
from app.models.mission import Mission
from app.db.database import SessionLocal
from datetime import date
app=FastAPI()
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
