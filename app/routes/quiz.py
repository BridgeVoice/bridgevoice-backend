import json
import os

from fastapi import APIRouter, HTTPException
from groq import Groq
from pydantic import BaseModel

router = APIRouter()

# Creates the Groq client using the API key stored in .env
client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))


# Defines the quiz level sent by the frontend
class QuizRequest(BaseModel):
    level: int


# Generates quiz questions for the selected level
@router.post("/quiz")
def generate_quiz(data: QuizRequest):

    # Maps each numeric level to its English difficulty
    level_names = {
        1: "Beginner",
        2: "Elementary",
        3: "Intermediate",
        4: "Advanced",
        5: "Expert",
    }

    level_name = level_names.get(data.level)

    # Rejects invalid quiz levels
    if not level_name:
        raise HTTPException(
            status_code=400,
            detail="Quiz level must be between 1 and 5.",
        )

    # Prompt sent to the LLM
    prompt = f"""
Generate exactly 10 English vocabulary multiple-choice questions for {level_name} level learners.

Return ONLY valid JSON.

Use this format:

{{
  "questions": [
    {{
      "word": "Reliable",
      "correct": "Can be trusted",
      "options": [
        "Can be trusted",
        "Always late",
        "Very noisy",
        "Very expensive"
      ]
    }}
  ]
}}

Rules:
- Return exactly 10 questions.
- Each question must have one English word.
- Each question must have exactly 4 answer options.
- Only one option must be correct.
- The correct answer must appear in the options.
- All 4 options must be different.
- Do not include duplicate questions.
- Match the vocabulary difficulty to the {level_name} level.
- Do not include explanations.
- Do not include markdown.
- Do not include any text before or after the JSON.
"""

    try:
        # Sends the prompt to Groq
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=2000,
        )

        # Gets the JSON text returned by the LLM
        ai_response = completion.choices[0].message.content

        # Converts the JSON text into a Python dictionary
        quiz_data = json.loads(ai_response)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="The AI returned an invalid quiz format.",
        )

    except Exception as error:
        print(f"Quiz generation error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Failed to generate the quiz.",
        )

    # Gets the questions array from the AI response
    questions = quiz_data.get("questions")

    # Ensures exactly 10 questions were returned
    if not isinstance(questions, list) or len(questions) != 10:
        raise HTTPException(
            status_code=500,
            detail="The AI must return exactly 10 quiz questions.",
        )

    seen_words = set()

    # Validates every generated question
    for question in questions:

        if not isinstance(question, dict):
            raise HTTPException(
                status_code=500,
                detail="The AI returned an invalid question.",
            )

        word = question.get("word")
        correct = question.get("correct")
        options = question.get("options")

        # Confirms the required fields exist
        if not isinstance(word, str) or not word.strip():
            raise HTTPException(
                status_code=500,
                detail="A quiz question is missing a valid word.",
            )

        if not isinstance(correct, str) or not correct.strip():
            raise HTTPException(
                status_code=500,
                detail="A quiz question is missing a correct answer.",
            )

        # Confirms each question has exactly 4 options
        if not isinstance(options, list) or len(options) != 4:
            raise HTTPException(
                status_code=500,
                detail="Every quiz question must have exactly 4 options.",
            )

        # Confirms every option is valid text
        if not all(isinstance(option, str) and option.strip() for option in options):
            raise HTTPException(
                status_code=500,
                detail="Every quiz option must contain valid text.",
            )

        # Confirms the correct answer is included
        if correct not in options:
            raise HTTPException(
                status_code=500,
                detail="The correct answer must be included in the options.",
            )

        # Confirms the options are unique
        if len(set(options)) != 4:
            raise HTTPException(
                status_code=500,
                detail="Quiz options must not contain duplicates.",
            )

        # Confirms quiz words are not duplicated
        normalized_word = word.strip().lower()

        if normalized_word in seen_words:
            raise HTTPException(
                status_code=500,
                detail="The AI returned duplicate quiz questions.",
            )

        seen_words.add(normalized_word)

    # Returns only validated questions to the frontend
    return {
        "level": data.level,
        "level_name": level_name,
        "questions": questions,
    }