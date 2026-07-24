from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
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
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(grammar.router, prefix="/api", tags=["grammar"])
app.include_router(phrases.router, prefix="/api", tags=["phrases"])
app.include_router(tts.router, prefix="/api", tags=["tts"])
app.include_router(vocabulary.router, prefix="/api", tags=["vocabulary"])
app.include_router(interview.router, prefix="/api", tags=["interview"])
app.include_router(daily_challenge.router, prefix="/api", tags=["daily-challenge"])
app.include_router(quiz.router, prefix="/api", tags=["quiz"])
app.include_router(culture.router, prefix="/api", tags=["culture"])
app.include_router(leaderboard.router, prefix="/api", tags=["leaderboard"])
app.include_router(posts.router, prefix="/api", tags=["posts"])
app.include_router(study_buddies.router, prefix="/api", tags=["study-buddies"])
app.include_router(study_buddy_requests.router, prefix="/api", tags=["study-buddy-requests"])
app.include_router(messages.router, prefix="/api", tags=["messages"])


@app.get("/")
def root():
    return {"message": "BridgeVoice Backend is running!"}
