from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.database import get_db
from app.models import User, SessionHistory

router = APIRouter()

def calculate_streak(db: Session, email: str) -> int:
    session_dates = {
        session.created_at.date()
        for session in db.query(SessionHistory)
        .filter(SessionHistory.user_email == email)
        .all()
        if session.created_at
    }

    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)

    if today in session_dates:
        current_date = today
    elif yesterday in session_dates:
        current_date = yesterday
    else:
        current_date = None

    streak = 0
    while current_date and current_date in session_dates:
        streak += 1
        current_date -= timedelta(days=1)

    return streak

@router.get("/leaderboard")
def get_leaderboard(email: str, db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .order_by(User.total_xp.desc())
        .limit(20)
        .all()
    )

    leaderboard = []
    for i, u in enumerate(users):
        leaderboard.append({
            "rank": i + 1,
            "name": u.full_name,
            "email": u.email,
            "xp": u.total_xp,
            "streak": calculate_streak(db, u.email),
            "is_you": u.email == email,
        })

    return leaderboard