"""
Stage 1 (audio) — speech-to-text on reel audio via Groq's hosted Whisper.
"""
import os
from typing import Optional

import httpx

from app.config import settings


async def transcribe_audio(file_path: str) -> Optional[str]:
    if not settings.GROQ_API_KEY:
        print("GROQ_API_KEY not set — skipping transcription.")
        return None

    if not os.path.exists(file_path):
        print(f"Audio file not found: {file_path}")
        return None

    mime_type = (
        "audio/wav"
        if file_path.lower().endswith(".wav")
        else "audio/mpeg"
    )

    async with httpx.AsyncClient(timeout=60) as client:
        with open(file_path, "rb") as f:
            resp = await client.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}"
                },
                files={
                    "file": (
                        os.path.basename(file_path),
                        f,
                        mime_type,
                    )
                },
                data={
                    "model": settings.GROQ_WHISPER_MODEL
                },
            )

        resp.raise_for_status()
        return resp.json().get("text")