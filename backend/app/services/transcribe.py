"""
Stage 1 (audio) — speech-to-text on reel audio via Groq's hosted Whisper.
"""
import os
from typing import Optional

import httpx

from app.config import settings


async def transcribe_audio(file_path: str) -> Optional[str]:
    """Transcribe an audio file at file_path using Groq's Whisper endpoint."""
    if not settings.GROQ_API_KEY:
        print("[transcribe] GROQ_API_KEY not set — skipping transcription.")
        return None

    if not os.path.exists(file_path):
        print(f"[transcribe] File not found: {file_path}")
        return None

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            with open(file_path, "rb") as f:
                resp = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                    files={"file": (os.path.basename(file_path), f, "audio/mpeg")},
                    data={"model": settings.GROQ_WHISPER_MODEL},
                )
            resp.raise_for_status()
            return resp.json().get("text")
    except Exception as e:
        print(f"[transcribe] Failed: {e}")
        return None
