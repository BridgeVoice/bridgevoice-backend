from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends 
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import users
from app.routes import chat
from app.routes import grammar
from app.routes import phrases
from app.routes import tts
from app.routes import vocabulary
from app.routes import interview
from app.routes import daily_challenge
from app.routes import quiz 
from app.routes import culture
from app.routes import leaderboard
from app.routes import posts
from app.routes import study_buddies
from app.routes import study_buddy_requests, messages
from app.auth import get_current_user_email

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="BridgeVoice API")

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Routes
# users stays partially public (register/login); its protected endpoints are marked individually
app.include_router(users.router, prefix="/api/users", tags=["users"])

# Everything below requires a valid JWT
protected = [Depends(get_current_user_email)]
app.include_router(chat.router, prefix="/api", tags=["chat"], dependencies=protected)
app.include_router(grammar.router, prefix="/api", tags=["grammar"], dependencies=protected)
app.include_router(phrases.router, prefix="/api", tags=["phrases"], dependencies=protected)
app.include_router(tts.router, prefix="/api", tags=["tts"], dependencies=protected)
app.include_router(vocabulary.router, prefix="/api", tags=["vocabulary"], dependencies=protected)
app.include_router(interview.router, prefix="/api", tags=["interview"], dependencies=protected)
app.include_router(daily_challenge.router, prefix="/api", tags=["daily-challenge"], dependencies=protected)
app.include_router(quiz.router, prefix="/api", tags=["quiz"], dependencies=protected)
app.include_router(culture.router, prefix="/api", tags=["culture"], dependencies=protected)
app.include_router(leaderboard.router, prefix="/api", tags=["leaderboard"], dependencies=protected)
app.include_router(posts.router, prefix="/api", tags=["posts"], dependencies=protected)
app.include_router(study_buddies.router, prefix="/api", tags=["study-buddies"], dependencies=protected)
app.include_router(study_buddy_requests.router, prefix="/api", tags=["study-buddy-requests"], dependencies=protected)
app.include_router(messages.router, prefix="/api", tags=["messages"], dependencies=protected)

@app.get("/")
def root():
    return {"message": "BridgeVoice Backend is running!"}
