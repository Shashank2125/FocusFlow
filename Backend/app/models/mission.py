from sqlalchemy import Column,Integer,String,Date,ForeignKey,Boolean
from app.db.database import Base
from datetime import date
class Mission(Base):
    __tablename__="missions"
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"))
    title=Column(String)
    completed=Column(Boolean, default=False)
    mission_date=Column(Date,default=date.today)