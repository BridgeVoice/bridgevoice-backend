from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import users
from app.routes import chat
from app.routes import grammar

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="BridgeVoice API")

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(grammar.router, prefix="/api", tags=["grammar"])

@app.get("/")
def root():
    return {"message": "BridgeVoice Backend is running!"}