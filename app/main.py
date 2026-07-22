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
from app.routes import daily_challenge
from app.routes import quiz 

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
app.include_router(daily_challenge.router, prefix="/api", tags=["daily-challenge"])
app.include_router(quiz.router, prefix="/api", tags=["quiz"])


@app.get("/")
def root():
    return {"message": "BridgeVoice Backend is running!"}