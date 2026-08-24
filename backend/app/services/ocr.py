"""
Stage 1 (visual) — OCR on video frames to catch on-screen text overlays
(dates, program names) that audio transcription alone would miss.

Uses Tesseract (local, no API key needed, lower accuracy on stylised
reel text) by default. Set GOOGLE_CLOUD_VISION_API_KEY to use Cloud
Vision instead for better accuracy on stylised fonts/overlays.
"""
import os
from typing import List, Optional

import httpx

GOOGLE_CLOUD_VISION_API_KEY = os.getenv("GOOGLE_CLOUD_VISION_API_KEY", "")


def ocr_frame_tesseract(image_path: str) -> Optional[str]:
    """Run local Tesseract OCR on a single extracted video frame."""
    try:
        import pytesseract
        from PIL import Image

        if not os.path.exists(image_path):
            return None
        return pytesseract.image_to_string(Image.open(image_path)).strip() or None
    except ImportError:
        print("[ocr] pytesseract/Pillow not installed — add to requirements.txt to enable local OCR.")
        return None
    except Exception as e:
        print(f"[ocr] Tesseract failed on {image_path}: {e}")
        return None


async def ocr_frame_cloud_vision(image_bytes: bytes) -> Optional[str]:
    """Run Google Cloud Vision OCR on a single frame's raw image bytes."""
    if not GOOGLE_CLOUD_VISION_API_KEY:
        return None

    import base64

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_CLOUD_VISION_API_KEY}",
                json={
                    "requests": [
                        {
                            "image": {"content": base64.b64encode(image_bytes).decode()},
                            "features": [{"type": "TEXT_DETECTION"}],
                        }
                    ]
                },
            )
            resp.raise_for_status()
            data = resp.json()
        annotations = data.get("responses", [{}])[0].get("textAnnotations", [])
        return annotations[0]["description"] if annotations else None
    except Exception as e:
        print(f"[ocr] Cloud Vision failed: {e}")
        return None


def ocr_frames(frame_paths: List[str]) -> str:
    """
    Run OCR across multiple extracted frames and concatenate the results.
    Call this with frame paths from a reel-downloading/frame-extraction step
    (e.g. ffmpeg sampling one frame every N seconds) — not built here.
    """
    texts = []
    for path in frame_paths:
        text = ocr_frame_tesseract(path)
        if text:
            texts.append(text)
    return "\n".join(texts)
