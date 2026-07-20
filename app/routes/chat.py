from fastapi import APIRouter
from pydantic import BaseModel
import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

router = APIRouter()

# Tone instructions injected into the system prompt per character.
# These match characterData.js on the frontend.
PERSONALITY_TONES = {
    "happy": (
        "You are enthusiastic, warm, and very encouraging. "
        "Use exclamation points, celebrate effort, and keep energy high. "
        "Your coach name is Happy."
    ),
    "stern": (
        "You are strict, precise, and formal. "
        "Correct errors firmly but fairly. Do not use casual language or emojis. "
        "Your coach name is Stern."
    ),
    "professional": (
        "You are calm, polished, and businesslike. "
        "Use clear professional English. Keep responses focused and structured. "
        "Your coach name is Alex."
    ),
    "friendly": (
        "You are relaxed, supportive, and conversational. "
        "Use casual language, contractions, and a warm tone. "
        "Your coach name is Sam."
    ),
}

DEFAULT_TONE = PERSONALITY_TONES["friendly"]


class ChatMessage(BaseModel):
    message: str
    scenario: str = "General Conversation"
    personality: str = "friendly"   # NEW: character id from frontend


@router.post("/chat")
async def chat(data: ChatMessage):
    tone = PERSONALITY_TONES.get(data.personality, DEFAULT_TONE)

    system_prompt = f"""You are a BridgeVoice AI English conversation coach helping newcomers to Canada practice English.

PERSONALITY & TONE:
{tone}

CURRENT SCENARIO: {data.scenario}

RULES:
- Keep responses SHORT: 2-3 sentences maximum.
- If the user makes a grammar mistake, gently correct it in your reply.
- Always end with a question to keep the conversation going.
- Stay in character — your tone should match the personality above throughout."""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": data.message},
            ],
            max_tokens=200,
        )
        reply = completion.choices[0].message.content
        return {"reply": reply}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"reply": f"Error: {str(e)}"}
