from fastapi import APIRouter
from pydantic import BaseModel
from groq import Groq
import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
router = APIRouter()

class ChallengeRequest(BaseModel):
    native_language: str = "English"
    proficiency_level: str = "Beginner"

class FeedbackRequest(BaseModel):
    challenge_type: str
    challenge_instruction: str
    user_response: str
    native_language: str = "English"
    proficiency_level: str = "Beginner"

@router.post("/daily-challenge/generate")
async def generate_challenge(data: ChallengeRequest):
    try:
        today = datetime.now().strftime("%A, %B %d, %Y")
        random_seed = random.randint(1000, 9999)

        prompt = f"""You are an English learning coach for newcomers to Canada.

Today is {today}.
Session ID: {random_seed} — generate FRESH unique challenges different every time.
Student's native language: {data.native_language}
Student's English level: {data.proficiency_level}

IMPORTANT LANGUAGE RULE:
- Write ALL instructions and tips in BOTH English AND {data.native_language}
- Format: "English text | {data.native_language} translation"
- This helps the student understand better in their native language

Generate exactly 3 daily English challenges practical for life in Canada.

Respond ONLY with valid JSON, no markdown, no extra text:
{{
  "date": "{today}",
  "challenges": [
    {{
      "type": "Speaking",
      "icon": "🎙️",
      "title": "Short title here",
      "instruction": "Clear instruction in English | Same instruction in {data.native_language}",
      "example": "An example response in English",
      "tip": "Helpful tip in English | Same tip in {data.native_language}",
      "xp": 30
    }},
    {{
      "type": "Writing",
      "icon": "✍️",
      "title": "Short title here",
      "instruction": "Clear instruction in English | Same instruction in {data.native_language}",
      "example": "An example response in English",
      "tip": "Helpful tip in English | Same tip in {data.native_language}",
      "xp": 20
    }},
    {{
      "type": "Vocabulary",
      "icon": "📚",
      "title": "Short title here",
      "instruction": "Clear instruction in English | Same instruction in {data.native_language}",
      "words": ["word1", "word2", "word3"],
      "example": "An example using the words in English",
      "tip": "Helpful tip in English | Same tip in {data.native_language}",
      "xp": 25
    }}
  ]
}}

Make challenges:
- Relevant to daily Canadian life (work, shopping, healthcare, social)
- Appropriate for {data.proficiency_level} level
- Fresh and different every single generation
- Practical and immediately useful for newcomers"""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=1.1
        )

        response_text = completion.choices[0].message.content.strip()
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        response_text = response_text.strip()

        return json.loads(response_text)

    except Exception as e:
        print(f"Daily challenge error: {e}")
        return {
            "date": datetime.now().strftime("%A, %B %d, %Y"),
            "challenges": [
                {
                    "type": "Speaking",
                    "icon": "🎙️",
                    "title": "Introduce Yourself",
                    "instruction": "Speak for 30 seconds introducing yourself in English | 30 ਸਕਿੰਟਾਂ ਲਈ ਅੰਗਰੇਜ਼ੀ ਵਿੱਚ ਆਪਣੇ ਆਪ ਨੂੰ ਪੇਸ਼ ਕਰੋ",
                    "example": "Hi, my name is... I am from... I am learning English because...",
                    "tip": "Speak slowly and clearly! | ਹੌਲੀ ਅਤੇ ਸਾਫ਼ ਬੋਲੋ!",
                    "xp": 30
                },
                {
                    "type": "Writing",
                    "icon": "✍️",
                    "title": "Write About Your Day",
                    "instruction": "Write 2-3 sentences about what you did today | ਅੱਜ ਤੁਸੀਂ ਕੀ ਕੀਤਾ ਇਸ ਬਾਰੇ 2-3 ਵਾਕ ਲਿਖੋ",
                    "example": "Today I went to the grocery store. I bought vegetables and milk.",
                    "tip": "Use past tense verbs! | ਭੂਤਕਾਲ ਦੀਆਂ ਕਿਰਿਆਵਾਂ ਵਰਤੋ!",
                    "xp": 20
                },
                {
                    "type": "Vocabulary",
                    "icon": "📚",
                    "title": "Canadian Words",
                    "instruction": "Learn these 3 words and use them in sentences | ਇਹ 3 ਸ਼ਬਦ ਸਿੱਖੋ ਅਤੇ ਵਾਕਾਂ ਵਿੱਚ ਵਰਤੋ",
                    "words": ["polite", "appreciate", "community"],
                    "example": "Canadians are very polite. I appreciate your help. Our community is friendly.",
                    "tip": "Practice each word 3 times! | ਹਰੇਕ ਸ਼ਬਦ 3 ਵਾਰ ਅਭਿਆਸ ਕਰੋ!",
                    "xp": 25
                }
            ]
        }


@router.post("/daily-challenge/feedback")
async def get_challenge_feedback(data: FeedbackRequest):
    try:
        prompt = f"""You are a friendly English learning coach evaluating a student's response.

Challenge Type: {data.challenge_type}
Challenge Instruction: {data.challenge_instruction}
Student's Response: "{data.user_response}"
Student's Level: {data.proficiency_level}
Student's Native Language: {data.native_language}

Evaluate the response and provide constructive feedback. Be encouraging but honest.
If the response seems off-topic, irrelevant, or very short, give a low score and explain why.

Respond ONLY with valid JSON, no markdown:
{{
  "score": 85,
  "grade": "Good",
  "feedback_english": "2-3 sentences of specific feedback in English pointing out what was good and what needs improvement",
  "feedback_native": "Same feedback translated to {data.native_language}",
  "corrections": ["specific correction 1 if any", "specific correction 2 if any"],
  "encouragement": "One short encouraging sentence"
}}

Score guide:
- 90-100 = Excellent (response is complete, relevant, well-structured)
- 75-89 = Good (mostly correct with minor issues)
- 60-74 = Fair (relevant but needs improvement)
- 0-59 = Needs Practice (off-topic, too short, or incorrect)"""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.7
        )

        response_text = completion.choices[0].message.content.strip()
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        response_text = response_text.strip()

        return json.loads(response_text)

    except Exception as e:
        print(f"Feedback error: {e}")
        return {
            "score": 75,
            "grade": "Good",
            "feedback_english": "Good effort! Keep practicing your English every day.",
            "feedback_native": "Good effort! Keep practicing your English every day.",
            "corrections": [],
            "encouragement": "You're making great progress!"
        }


class TranslateRequest(BaseModel):
    challenges: list
    native_language: str

@router.post("/daily-challenge/translate")
async def translate_challenges(data: TranslateRequest):
    try:
        challenges_text = json.dumps(data.challenges)
        prompt = f"""Translate ONLY the instruction and tip fields of these challenges to {data.native_language}.
Keep everything else exactly the same (title, type, icon, example, words, xp).
Only add " | {data.native_language} translation" after each instruction and tip.

Challenges: {challenges_text}

Respond ONLY with valid JSON array of the same challenges with translated instruction and tip fields."""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.3
        )

        response_text = completion.choices[0].message.content.strip()
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        response_text = response_text.strip()

        translated = json.loads(response_text)
        return {"challenges": translated}

    except Exception as e:
        print(f"Translation error: {e}")
        return {"challenges": data.challenges}