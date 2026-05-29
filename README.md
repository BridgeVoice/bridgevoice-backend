# BridgeVoice Backend

AI-Powered English Conversation Learning Platform — Backend API

## Tech Stack
- Python 3.14
- FastAPI
- SQLite
- SQLAlchemy
- JWT Authentication
- LanguageTool API (Grammar Checking)
- Google Gemini AI (Chat & Grammar)

## Setup Instructions

1. Clone the repository
2. Create virtual environment:
   py -3 -m venv venv
3. Activate virtual environment:
   venv\Scripts\activate
4. Install packages:
   pip install -r requirements.txt
5. Run the server:
   uvicorn app.main:app --reload
6. Visit API docs:
   http://127.0.0.1:8000/docs

## API Endpoints

### Users
- POST /api/users/register — Register new user
- POST /api/users/login — Login and get token
- GET /api/users/profile — Get user profile

### Chat
- POST /api/chat — AI conversation

### Grammar
- POST /api/grammar — Check grammar mistakes

## Team
- Gitanshu — Backend & Infrastructure
- Juno — Frontend
- Group 4 — INFO6156 Capstone
