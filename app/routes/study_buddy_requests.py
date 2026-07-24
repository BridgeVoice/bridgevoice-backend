from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, StudyBuddyRequest

router = APIRouter()

@router.post("/study-buddies/request")
def send_request(data: dict, db: Session = Depends(get_db)):
    from_email = data.get("from_email")
    to_email = data.get("to_email")

    if not from_email or not to_email:
        raise HTTPException(status_code=400, detail="Missing from_email or to_email")

    existing = db.query(StudyBuddyRequest).filter(
        StudyBuddyRequest.from_email == from_email,
        StudyBuddyRequest.to_email == to_email
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Request already sent")

    req = StudyBuddyRequest(from_email=from_email, to_email=to_email, status="pending")
    db.add(req)
    db.commit()
    db.refresh(req)

    return {"message": "Request sent", "id": req.id}

@router.get("/study-buddies/requests")
def get_requests(email: str, db: Session = Depends(get_db)):
    incoming_raw = db.query(StudyBuddyRequest).filter(
        StudyBuddyRequest.to_email == email,
        StudyBuddyRequest.status == "pending"
    ).all()

    sent_raw = db.query(StudyBuddyRequest).filter(
        StudyBuddyRequest.from_email == email
    ).all()

    incoming = []
    for r in incoming_raw:
        sender = db.query(User).filter(User.email == r.from_email).first()
        incoming.append({
            "id": r.id,
            "from_email": r.from_email,
            "from_name": sender.full_name if sender else "Unknown",
            "from_language": sender.language_background if sender else None,
            "from_level": sender.proficiency_level if sender else None,
            "from_goals": sender.goals if sender else None,
        })

    sent = [{"id": r.id, "to_email": r.to_email, "status": r.status} for r in sent_raw]

    return {"incoming": incoming, "sent": sent}

@router.patch("/study-buddies/request/{request_id}")
def respond_to_request(request_id: int, data: dict, db: Session = Depends(get_db)):
    action = data.get("action")
    if action not in ("accept", "reject"):
        raise HTTPException(status_code=400, detail="action must be 'accept' or 'reject'")

    req = db.query(StudyBuddyRequest).filter(StudyBuddyRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    req.status = "accepted" if action == "accept" else "rejected"
    db.commit()
    db.refresh(req)

    return {"message": f"Request {req.status}"}

@router.get("/study-buddies/connected")
def get_connected(email: str, db: Session = Depends(get_db)):
    accepted = db.query(StudyBuddyRequest).filter(
        StudyBuddyRequest.status == "accepted",
        (StudyBuddyRequest.from_email == email) | (StudyBuddyRequest.to_email == email)
    ).all()

    buddies = []
    for r in accepted:
        other_email = r.to_email if r.from_email == email else r.from_email
        user = db.query(User).filter(User.email == other_email).first()
        if user:
            buddies.append({
                "email": user.email,
                "full_name": user.full_name,
                "initial": user.full_name[0].upper() if user.full_name else "?",
                "language_background": user.language_background,
                "proficiency_level": user.proficiency_level,
            })

    return buddies