from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str
    language_background: Optional[str] = None
    proficiency_level: Optional[str] = None
    goals: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    language_background: Optional[str] = None
    proficiency_level: Optional[str] = None
    goals: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str