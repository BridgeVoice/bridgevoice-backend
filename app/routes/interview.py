import os
import json
from groq import Groq

from fastapi import APIRouter
from pydantic import BaseModel

# Creates a router for interview-related endpoints
router = APIRouter()

# Creates the Groq client using the API key stored in the .env file
client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))


def clean_json_text(raw: str) -> str:
    """Strips markdown code fences if the model ignores instructions."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    return raw


# ---------------------------------------------------------------
# 1) GENERATE QUESTIONS — different questions per job category
# ---------------------------------------------------------------

class QuestionRequest(BaseModel):
    job_type: str


@router.post("/interview/questions")
def interview_questions(data: QuestionRequest):

    prompt = f"""Generate exactly 5 job interview questions for a "{data.job_type}" position in Canada.

The candidate is an English learner (a newcomer to Canada), so keep the wording
clear, natural, and free of idioms that are hard to understand.

Rules:
- Question 1 must be a "tell me about yourself" style opener.
- Questions 2-4 must be specific to the {data.job_type} role.
- Question 5 must be about motivation (why this job / this company).

Return ONLY valid JSON. Do not add markdown. Do not add explanations.
Do not add text before or after the JSON.

Format:
["question 1", "question 2", "question 3", "question 4", "question 5"]"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.8,  # a little variety so repeat practice isn't identical
        )
        raw = clean_json_text(completion.choices[0].message.content)
        questions = json.loads(raw)

        # Validate the shape before trusting it
        if not isinstance(questions, list) or len(questions) == 0:
            raise ValueError("Model did not return a list of questions")
        questions = [str(q) for q in questions][:5]

        return {"job_type": data.job_type, "questions": questions}

    except Exception as e:
        import traceback
        traceback.print_exc()
        # Frontend checks for "error" and falls back to hard-coded questions
        return {"error": str(e)}


# ---------------------------------------------------------------
# 2) FEEDBACK — score and coach the user's answers
# ---------------------------------------------------------------

class InterviewAnswer(BaseModel):
    question: str
    answer: str


class FeedbackRequest(BaseModel):
    job_type: str
    answers: list[InterviewAnswer]


@router.post("/interview/feedback")
def interview_feedback(data: FeedbackRequest):

    qa_text = "\n\n".join(
        f'Question {i + 1}: {a.question}\nAnswer {i + 1}: {a.answer or "(no answer given)"}'
        for i, a in enumerate(data.answers)
    )

    prompt = f"""You are a professional but encouraging interview coach evaluating a
candidate applying for a "{data.job_type}" position in Canada.
The candidate is an English learner, so gently note grammar issues when relevant,
but focus mainly on the content and structure of each answer.

Here are the questions and the candidate's answers:

{qa_text}

Score each answer from 0 to 100:
- 80-100: specific, detailed, relevant, well structured
- 60-79: relevant but could use more detail or examples
- 0-59: too short, vague, off-topic, or missing

Return ONLY valid JSON. Do not add markdown. Do not add explanations.
Do not add text before or after the JSON. Return one object per answer,
in the same order as the questions above.

Format:
[
    {{
        "score": 0,
        "tip": ""
    }}
]

Keep each tip to 1-2 sentences, specific to that answer, and encouraging."""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
        )
        raw = clean_json_text(completion.choices[0].message.content)
        results = json.loads(raw)

        if not isinstance(results, list) or len(results) == 0:
            raise ValueError("Model did not return a list of results")

        # Pair model scores back with the original questions/answers so the
        # frontend never depends on the model echoing text back correctly.
        scores = []
        for i, a in enumerate(data.answers):
            r = results[i] if i < len(results) else {}
            score = int(r.get("score", 50))
            score = max(0, min(100, score))  # clamp to 0-100
            scores.append({
                "question": a.question,
                "answer": a.answer,
                "score": score,
                "tip": str(r.get("tip", "Keep practicing — add specific examples.")),
            })

        avg_score = round(sum(s["score"] for s in scores) / len(scores))

        return {"scores": scores, "avgScore": avg_score}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
