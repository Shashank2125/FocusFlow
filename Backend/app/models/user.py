from sqlalchemy import Column, Integer, String, DateTime
from app.db.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    rank = Column(String, default="E")
    xp = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
