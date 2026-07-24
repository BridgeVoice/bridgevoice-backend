from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    language_background: Optional[str] = None
    proficiency_level: Optional[str] = None
    goals: Optional[str] = None
    daily_goal: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return password

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    language_background: Optional[str] = None
    proficiency_level: Optional[str] = None
    goals: Optional[str] = None
    daily_goal: Optional[str] = None
    sessions_completed: Optional[int] = 0
    total_xp: Optional[int] = 0
    # Number of consecutive days the user has completed at least one session
    day_streak: Optional[int] = 0
    email_sent: Optional[bool] = None

    class Config:
        from_attributes = True

class OnboardingUpdate(BaseModel):
    email: EmailStr
    language_background: str
    proficiency_level: str
    goals: str
    daily_goal: Optional[str] = None 

class ActivityComplete(BaseModel):
    email: EmailStr
    xp_earned: int

class Token(BaseModel):
    access_token: str
    token_type: str

class SessionHistoryCreate(BaseModel):
    email: EmailStr
    activity_name: str
    score: int
    xp_earned: int

class SessionHistoryResponse(BaseModel):
    activity_name: str
    score: int
    xp_earned: int
    created_at: datetime

    class Config:
        from_attributes = True

class PostCreate(BaseModel):
    user_email: str
    content: str

class PostResponse(BaseModel):
    id: int
    user_email: str
    content: str
    likes: int
    created_at: datetime
    full_name: str

    class Config:
        from_attributes = True

class StudyBuddyResponse(BaseModel):
    email: str
    full_name: str
    language_background: Optional[str] = None
    proficiency_level: Optional[str] = None
    goals: Optional[str] = None
    compatibility_score: int

    class Config:
        from_attributes = True