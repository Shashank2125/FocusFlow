from sqlalchemy import Column,Integer,String,Date,ForeignKey,Boolean,Enum
from app.db.database import Base
from datetime import date
import enum
class MissionDifficulty(enum.Enum):
    EASY="EASY"
    NORMAL="NORMAL"
    HARD="HARD"
class Mission(Base):
    __tablename__="missions"
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"))
    title=Column(String)
    completed=Column(Boolean, default=False)
    mission_date=Column(Date,default=date.today)

    #new difficulty column
    difficulty=Column(
        Enum(MissionDifficulty),
        default=MissionDifficulty.NORMAL,
        nullable=False
    )
