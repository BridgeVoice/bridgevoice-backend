# Groq Orpheus TTS — uses the same GROQ_API_KEY already in .env
# Model:  canopylabs/orpheus-v1-english
# Voices: autumn (Friendly), hannah (Happy), austin (Stern), daniel (Professional)
# Supports vocal directions like [cheerful] prepended to text for Happy

from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel
import os, re, io, wave
from groq import Groq

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

TTS_MODEL  = "canopylabs/orpheus-v1-english"
MAX_CHARS  = 180   # Orpheus hard limit is 200; keep margin for direction tag

# Voice per character — matches characterData.js on the frontend
VOICE_CONFIG = {
    "happy":        {"voice": "hannah",  "direction": "[cheerful] "},  # female ✅
    "stern":        {"voice": "austin",  "direction": ""},              # male   ✅
    "professional": {"voice": "diana",   "direction": ""},              # female (was daniel male ❌)
    "friendly":     {"voice": "troy",    "direction": ""},              # male   (was autumn female ❌)
}


def split_into_chunks(text: str, max_chars: int = MAX_CHARS) -> list[str]:
    """
    Split text at sentence boundaries so each chunk ≤ max_chars.
    Falls back to comma splits, then hard truncation.
    """
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    chunks, current = [], ""
    # Split at sentence endings
    for sentence in re.split(r'(?<=[.!?])\s+', text):
        candidate = (current + " " + sentence).strip() if current else sentence
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            # Single sentence too long — split at commas
            if len(sentence) > max_chars:
                current = ""
                for clause in re.split(r',\s*', sentence):
                    c2 = (current + ", " + clause).strip(", ") if current else clause
                    if len(c2) <= max_chars:
                        current = c2
                    else:
                        if current:
                            chunks.append(current)
                        current = clause[:max_chars]
            else:
                current = sentence

    if current:
        chunks.append(current)
    return chunks or [text[:max_chars]]


def join_wav_bytes(wav_list: list[bytes]) -> bytes:
    """Concatenate multiple WAV byte blobs into a single WAV."""
    if len(wav_list) == 1:
        return wav_list[0]
    buf = io.BytesIO()
    with wave.open(buf, "wb") as out:
        ready = False
        for blob in wav_list:
            try:
                with wave.open(io.BytesIO(blob), "rb") as src:
                    if not ready:
                        out.setparams(src.getparams())
                        ready = True
                    out.writeframes(src.readframes(src.getnframes()))
            except Exception as e:
                print(f"WAV chunk skip: {e}")
    return buf.getvalue()


class TTSRequest(BaseModel):
    text:        str
    personality: str = "friendly"


@router.post("/tts")
async def text_to_speech(data: TTSRequest):
    config    = VOICE_CONFIG.get(data.personality, VOICE_CONFIG["friendly"])
    voice     = config["voice"]
    direction = config["direction"]

    chunks    = split_into_chunks(data.text)
    wav_parts = []

    for chunk in chunks:
        input_text = direction + chunk
        try:
            resp      = client.audio.speech.create(
                model           = TTS_MODEL,
                voice           = voice,
                input           = input_text,
                response_format = "wav",
            )
            wav_parts.append(resp.content)
        except Exception as e:
            print(f"Groq TTS error on chunk '{chunk[:40]}...': {e}")

    if not wav_parts:
        # Return 204 — frontend will fall back to browser TTS
        return Response(status_code=204)

    audio = join_wav_bytes(wav_parts)
    return Response(content=audio, media_type="audio/wav")
