from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import (UserRegister, UserLogin, UserResponse, Token, OnboardingUpdate, ActivityComplete)
from app.auth import hash_password, verify_password, create_access_token
from app.email_service import send_welcome_email 

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hash_password(user.password),
        language_background=user.language_background,
        proficiency_level=user.proficiency_level,
        goals=user.goals,
        daily_goal=user.daily_goal
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    email_sent = send_welcome_email(
        to_email=new_user.email,
        full_name=new_user.full_name
    )

    return {
    **new_user.__dict__,
    "email_sent": email_sent
    } 

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    # Check password
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    # Create token
    token = create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/profile", response_model=UserResponse)
def get_profile(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/onboarding", response_model=UserResponse)
def update_onboarding(data: OnboardingUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.language_background = data.language_background
    user.proficiency_level = data.proficiency_level
    user.goals = data.goals
    user.daily_goal = data.daily_goal

    db.commit()
    db.refresh(user)

    return user

@router.post("/complete-activity")
def complete_activity(data: ActivityComplete, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.sessions_completed += 1
    user.total_xp += data.xp_earned

    db.commit()
    db.refresh(user)

    return {
        "sessions_completed": user.sessions_completed,
        "total_xp": user.total_xp
    }