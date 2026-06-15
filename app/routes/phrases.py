from fastapi import APIRouter
from pydantic import BaseModel
from groq import Groq
import os
import json 

router = APIRouter()

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))


class PhraseRequest(BaseModel):
    category: str 

@router.post("/phrases")
async def generate_phrases(data: PhraseRequest):
    try:
        prompt = f"""
        Generate exactly 5 useful English phrases for newcomers to Canada in the category: {data.category}.

        Return ONLY valid JSON. 

        Format:

        [
         {{
             "phrase": "",
             "meaning": "",
             "example": "",
             "tip": ""
         }}
        ] 

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
            max_tokens=500
        ) 

        ai_response = completion.choices[0].message.content
        phrases = json.loads(ai_response)

        return {
            "phrases": phrases
        }

    except Exception as e:
        return {
            "error": str(e)
        }