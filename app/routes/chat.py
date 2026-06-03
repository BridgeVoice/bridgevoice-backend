from fastapi import APIRouter
from pydantic import BaseModel
import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    scenario: str = "General Conversation"

@router.post("/chat")
async def chat(data: ChatMessage):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a friendly English conversation coach helping people practice English.
Current scenario: {data.scenario}
Keep responses short (2-3 sentences max), encouraging, and conversational.
If the user makes grammar mistakes, gently correct them.
Always end with a question to keep the conversation going."""
                },
                {
                    "role": "user",
                    "content": data.message
                }
            ],
            max_tokens=200
        )
        reply = completion.choices[0].message.content
        return {"reply": reply}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"reply": f"Error: {str(e)}"}
        return {"reply": "I'm having trouble right now. Please try again!"}