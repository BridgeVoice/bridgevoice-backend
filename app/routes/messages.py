from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Message

router = APIRouter()

@router.get("/messages/{other_email}")
def get_conversation(other_email: str, email: str, db: Session = Depends(get_db)):
    messages = (
        db.query(Message)
        .filter(
            ((Message.from_email == email) & (Message.to_email == other_email)) |
            ((Message.from_email == other_email) & (Message.to_email == email))
        )
        .order_by(Message.created_at.asc())
        .all()
    )

    result = []
    for m in messages:
        result.append({
            "id": m.id,
            "from_email": m.from_email,
            "content": m.content,
            "created_at": m.created_at.strftime("%I:%M %p"),
            "is_mine": m.from_email == email,
        })

    return result

@router.post("/messages/send")
def send_message(data: dict, db: Session = Depends(get_db)):
    from_email = data.get("from_email")
    to_email = data.get("to_email")
    content = data.get("content")

    message = Message(from_email=from_email, to_email=to_email, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)

    return {"message": "Sent", "id": message.id}