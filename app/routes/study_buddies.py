from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, StudyBuddyRequest

router = APIRouter()

def compatibility_score(me: User, other: User) -> int:
    score = 0

    if me.proficiency_level and other.proficiency_level:
        if me.proficiency_level == other.proficiency_level:
            score += 2

    if me.language_background and other.language_background:
        if me.language_background != other.language_background:
            score += 2

    if me.goals and other.goals:
        if me.goals == other.goals:
            score += 1

    return score

@router.get("/study-buddies")
def get_study_buddy_suggestions(email: str, db: Session = Depends(get_db)):
    me = db.query(User).filter(User.email == email).first()
    if not me:
        return []

    # Emails already connected or with a pending/rejected request either direction
    existing = db.query(StudyBuddyRequest).filter(
        (StudyBuddyRequest.from_email == email) | (StudyBuddyRequest.to_email == email)
    ).all()
    excluded_emails = {r.from_email for r in existing} | {r.to_email for r in existing}
    excluded_emails.add(email)

    candidates = db.query(User).filter(User.email.notin_(excluded_emails)).all()

    results = []
    for other in candidates:
        results.append({
            "email": other.email,
            "full_name": other.full_name,
            "language_background": other.language_background,
            "proficiency_level": other.proficiency_level,
            "goals": other.goals,
            "compatibility_score": compatibility_score(me, other),
        })

    results.sort(key=lambda r: r["compatibility_score"], reverse=True)
    return results[:10]