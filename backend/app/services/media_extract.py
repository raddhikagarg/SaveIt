"""
Media extraction for SaveIt.

Downloads media from supported URLs (currently Instagram via yt-dlp),
extracts useful metadata/caption, converts audio for transcription,
and returns combined text for the LLM extraction pipeline.
"""

import asyncio
import os
import tempfile
from typing import Optional

import yt_dlp

from app.services.transcribe import transcribe_audio


def _download_media(url: str, output_dir: str) -> dict:
    """Download media and return yt-dlp metadata."""

    output_template = os.path.join(output_dir, "media.%(ext)s")

    options = {
        "outtmpl": output_template,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)

    return info


async def extract_media_text(url: str) -> Optional[str]:
    """
    Download media, collect its caption/metadata, transcribe its audio,
    and return combined text suitable for the LLM.
    """

    if not url:
        return None

    try:
        with tempfile.TemporaryDirectory(prefix="saveit_media_") as temp_dir:

            # yt-dlp is synchronous, so run it in a worker thread.
            info = await asyncio.to_thread(
                _download_media,
                url,
                temp_dir,
            )

            parts = []

            # Instagram caption / description
            description = info.get("description")
            if description:
                parts.append(f"Caption:\n{description}")

            # Uploader/channel
            uploader = info.get("uploader") or info.get("channel")
            if uploader:
                parts.append(f"Creator: {uploader}")

            # Find downloaded media file
            media_file = None

            for filename in os.listdir(temp_dir):
                if filename.lower().endswith(
                    (".mp4", ".mkv", ".webm", ".mov", ".avi")
                ):
                    media_file = os.path.join(temp_dir, filename)
                    break

            if media_file:
                audio_file = os.path.join(temp_dir, "audio.wav")

                process = await asyncio.create_subprocess_exec(
                    "ffmpeg",
                    "-y",
                    "-i",
                    media_file,
                    "-vn",
                    "-acodec",
                    "pcm_s16le",
                    audio_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                _, stderr = await process.communicate()

                if process.returncode == 0 and os.path.exists(audio_file):
                    transcript = await transcribe_audio(audio_file)

                    if transcript:
                        parts.append(f"Transcript:\n{transcript}")
                else:
                    print(
                        "[media_extract] FFmpeg failed:",
                        stderr.decode(errors="ignore")[-1000:],
                    )

            if not parts:
                return None

            return "\n\n".join(parts)

    except Exception as e:
        print(f"[media_extract] Failed to process {url}: {e}")
        return None