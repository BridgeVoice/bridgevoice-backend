from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    language_background = Column(String, nullable=True)
    proficiency_level = Column(String, nullable=True)
    goals = Column(String, nullable=True)
    daily_goal = Column(String, nullable=True)
    sessions_completed = Column(Integer, default=0)
    total_xp = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now()) 

class SessionHistory(Base):
    __tablename__ = "session_history"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False)
    activity_name = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    xp_earned = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())