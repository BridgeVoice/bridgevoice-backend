from fastapi import APIRouter
from pydantic import BaseModel
import requests

router = APIRouter()

class GrammarRequest(BaseModel):
    text: str

@router.post("/grammar")
async def check_grammar(data: GrammarRequest):
    try:
        response = requests.post(
            'https://api.languagetool.org/v2/check',
            data={
                'text': data.text,
                'language': 'en-CA',
            }
        )
        result = response.json()

        errors = []
        corrected = data.text

        for match in result.get('matches', []):
            wrong = data.text[match['offset']:match['offset'] + match['length']]
            if match['replacements']:
                correct = match['replacements'][0]['value']
                rule = match['message']
                errors.append({
                    'wrong': wrong,
                    'correct': correct,
                    'rule': rule
                })
                corrected = corrected.replace(wrong, correct, 1)

        total = len(result.get('matches', []))
        score = max(0, 100 - (total * 10))

        if total == 0:
            feedback = "Perfect! No grammar mistakes found. Your English is excellent!"
        elif total <= 2:
            feedback = f"Good job! Only {total} small mistake(s). Keep practicing!"
        elif total <= 5:
            feedback = f"Nice try! Found {total} mistakes. Focus on tenses and articles."
        else:
            feedback = f"Keep practicing! Found {total} mistakes. Review basic grammar rules."

        return {
            "corrected": corrected,
            "score": score,
            "errors": errors,
            "feedback": feedback
        }

    except Exception as e:
        print(f"Grammar error: {e}")
        return {
            "corrected": data.text,
            "score": 0,
            "errors": [],
            "feedback": "Could not check grammar right now. Please try again!"
        }