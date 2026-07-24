from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, timezone, timedelta
from app.database import get_db
from app.models import User, SessionHistory, Post, StudyBuddyRequest, Message
from app.schemas import (UserRegister, UserLogin, UserResponse, Token, OnboardingUpdate, ActivityComplete, SessionHistoryCreate,
    SessionHistoryResponse,  DailyChallengeComplete)
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

    # Gets every unique day on which the user completed a session
    session_dates = {
        session.created_at.date()
        for session in db.query(SessionHistory)
        .filter(SessionHistory.user_email == email)
        .all()
        if session.created_at
    }

    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)

    # A streak remains active if the user practised today or yesterday
    if today in session_dates:
        current_date = today
    elif yesterday in session_dates:
        current_date = yesterday
    else:
        current_date = None

    day_streak = 0

    # Counts backwards through consecutive practice days
    while current_date and current_date in session_dates:
        day_streak += 1
        current_date -= timedelta(days=1)

    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "language_background": user.language_background,
        "proficiency_level": user.proficiency_level,
        "goals": user.goals,
        "daily_goal": user.daily_goal,
        "sessions_completed": user.sessions_completed,
        "total_xp": user.total_xp,
        "day_streak": day_streak,
        "email_sent": None
    }

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

@router.post("/session-history")
def save_session(data: SessionHistoryCreate, db: Session = Depends(get_db)):

    session = SessionHistory(
        user_email=data.email,
        activity_name=data.activity_name,
        score=data.score,
        xp_earned=data.xp_earned
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return {"message": "Session saved"}

#GET endpoint added
@router.get("/session-history/{email}",
            response_model=list[SessionHistoryResponse])
def get_session_history(email: str, db: Session = Depends(get_db)):

    sessions = (
        db.query(SessionHistory)
        .filter(SessionHistory.user_email == email)
        .order_by(SessionHistory.created_at.desc())
        .limit(5)
        .all()
    )

    return sessions 

#todays session on Daily Goal Progress
@router.get("/today-sessions/{email}")
def get_today_sessions(email: str, db: Session = Depends(get_db)):

    today_utc = datetime.now(timezone.utc).date()

    start_of_day = datetime.combine(
        today_utc,
        datetime.min.time()
    )

    end_of_day = start_of_day + timedelta(days=1)

    count = db.query(SessionHistory).filter(
        SessionHistory.user_email == email,
        SessionHistory.created_at >= start_of_day,
        SessionHistory.created_at < end_of_day
    ).count()

    return {"today_sessions": count}

from app.schemas import ChangePasswordRequest

@router.put("/change-password")
def change_password(data: ChangePasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters long")

    user.hashed_password = hash_password(data.new_password)
    db.commit()

    return {"message": "Password updated"}


@router.post("/complete-daily-challenge")
def complete_daily_challenge(
    data: DailyChallengeComplete,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(
        status_code=404,
        detail="User not found"
        )

    today_utc = datetime.now(timezone.utc).date()

    start_of_day = datetime.combine(
        today_utc,
        datetime.min.time()
    )

    end_of_day = start_of_day + timedelta(days=1)

    existing_challenge = db.query(SessionHistory).filter(
        SessionHistory.user_email == data.email,
        SessionHistory.activity_name == "Daily Challenge",
        SessionHistory.created_at >= start_of_day,
        SessionHistory.created_at < end_of_day
    ).first()

    # Prevents the same Daily Challenge from awarding XP more than once per day
    if existing_challenge:
        return {
            "already_completed": True,
            "message": "Daily Challenge already completed today.",
            "sessions_completed": user.sessions_completed,
            "total_xp": user.total_xp
        }
    
    # Awards the full Daily Challenge reward once
    user.sessions_completed += 1
    user.total_xp += 75 

    # Saves one Daily Challenge session in recent history
    session = SessionHistory(
        user_email=data.email,
        activity_name="Daily Challenge",
        score=data.score,
        xp_earned=75
    )

    db.add(session)

    # Saves the XP update and session history together
    db.commit()
    db.refresh(user)

    return {
        "already_completed": False,
        "message": "Daily Challenge completed successfully.",
        "sessions_completed": user.sessions_completed,
        "total_xp": user.total_xp,
        "xp_earned": 75,
        "score": data.score
    }

