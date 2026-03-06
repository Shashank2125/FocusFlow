from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean
from app.db.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    rank = Column(String, default="E")
    xp = Column(Integer, default=0)
    streak=Column(Integer,default=0)
    last_active = Column(DateTime, nullable=True) 
    created_at = Column(DateTime, default=datetime.utcnow)
    daily_xp=Column(Integer,default=0)
    last_xp_date=Column(Date,nullable=True)
    phase=Column(String,default="Ignition")
    xp_debt = Column(Integer, default=0)
    overdrive_active = Column(Boolean, default=False)
    overdrive_expires = Column(Date, nullable=True)
    current_state = Column(String, default="Recovery")




