import os
import json
from groq import Groq

from fastapi import APIRouter
from pydantic import BaseModel

# Creates a router for vocabulary-related endpoints
router = APIRouter()

# Creates the Groq client using the API key stored in the .env file
client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))


# Defines the data the frontend will send to this endpoint
class VocabularyRequest(BaseModel):
    topic: str


# Receives a topic and returns vocabulary for that topic
@router.post("/vocabulary")
def get_vocabulary(data: VocabularyRequest):

    # Prompt sent to the AI model
    prompt = f"""
    Generate exactly 5 English vocabulary words for the topic: {data.topic}.

    Return ONLY valid JSON.

    Format:

    [
        {{
            "word": "",
            "meaning": "",
            "example": ""
        }}
    ]

    Do not add markdown.
    Do not add explanations.
    Do not add text before or after the JSON.
    """

    # Send the prompt to Groq and generate vocabulary
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
    )

    # Extract the AI response text
    ai_response = completion.choices[0].message.content

    # Temporary debug print so we can see exactly what Groq returned
    print(ai_response)

    # Convert the AI response from JSON text into Python data
    words = json.loads(ai_response)

    # Return the topic and AI-generated vocabulary to the frontend
    return {"topic": data.topic, "words": words}
