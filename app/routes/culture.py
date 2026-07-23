from fastapi import APIRouter
from pydantic import BaseModel
from groq import Groq
import os
import json

router = APIRouter()

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))


class CultureRequest(BaseModel):
    category: str
    province: str = ""


@router.post("/culture")
async def generate_culture_content(data: CultureRequest):
    try:
        prompt = f"""
       {"Focus specifically on the province of " + data.province + ", Canada." if data.province else "Focus on Canada in general, not any specific province."}
        Generate exactly 5 helpful guide entries about Canadian culture for newcomers in the category: {data.category}.

        Each entry teaches one specific, practical aspect of Canadian life in that category.
        Write in simple, clear English suitable for English language learners.

        Return ONLY valid JSON.

        Format:

        [
         {{
             "title": "",
             "content": "",
             "tip": ""
         }}
        ]

        "title" is a short heading (under 8 words).
        "content" is 2-4 sentences of practical explanation.
        "tip" is one actionable sentence of advice.

        Do not add markdown.
        Do not add explanations.
        Do not add text before or after the JSON.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=800
        )

        ai_response = completion.choices[0].message.content
        entries = json.loads(ai_response)

        return {
            "entries": entries
        }

    except Exception as e:
        return {
            "error": str(e)
        }