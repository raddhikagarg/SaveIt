"""
Stage 1 (audio) — speech-to-text on reel audio via Whisper.

Requires a downloaded media file (audio track extracted from the reel).
Wire in real reel-downloading before this is called with an actual file;
for now this degrades gracefully (returns None) if no ANTHROPIC/OPENAI
Whisper access is configured, so the rest of the pipeline still runs.
"""
import os
from typing import Optional

import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


async def transcribe_audio(file_path: str) -> Optional[str]:
    """
    Transcribe an audio file at file_path using OpenAI's Whisper API.
    Returns the transcript text, or None if unavailable/not configured.
    """
    if not OPENAI_API_KEY:
        print("[transcribe] OPENAI_API_KEY not set — skipping transcription.")
        return None

    if not os.path.exists(file_path):
        print(f"[transcribe] File not found: {file_path}")
        return None

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            with open(file_path, "rb") as f:
                resp = await client.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                    files={"file": (os.path.basename(file_path), f, "audio/mpeg")},
                    data={"model": "whisper-1"},
                )
            resp.raise_for_status()
            return resp.json().get("text")
    except Exception as e:
        print(f"[transcribe] Failed: {e}")
        return None
