from fastapi import FastAPI
from app.db.database import engine
from app.models.user import User, Base
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
