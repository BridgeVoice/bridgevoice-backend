from fastapi import APIRouter
from pydantic import BaseModel
import google.generativeai as genai

import os
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
model = genai.GenerativeModel("gemini-2.0-flash")

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    scenario: str = "General Conversation"

@router.post("/chat")
async def chat(data: ChatMessage):
    try:
        prompt = f"""You are a friendly English conversation coach helping newcomers to Canada practice English.
Current scenario: {data.scenario}
Keep responses short (2-3 sentences max), encouraging, and conversational.
If the user makes grammar mistakes, gently correct them.
Always end with a question to keep the conversation going.

User said: {data.message}

Respond naturally as the AI coach:"""

        response = model.generate_content(prompt)
        return {"reply": response.text}
    except Exception as e:
        print(f"Gemini error: {e}")
        return {"reply": f"Error: {str(e)}"}