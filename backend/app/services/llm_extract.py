"""
Core extraction logic for SaveIt.

Contains:
- Stage 2: linked-page scraping (a landing page is treated as higher-trust
  than the reel itself when both exist).
- The single LLM structured-extraction call used by every stage.
- run_extraction_pipeline(): orchestrates Stage 1 (raw text already in hand)
  -> Stage 2 (linked page) -> Stage 3 (search_fallback service) and returns
  a final ExtractionResult.
"""
import json
import re
from datetime import datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from app.config import settings
from app.models import Category
from app.schemas import ExtractionResult
from app.services.search_fallback import search_for_deadline

CONFIDENCE_THRESHOLD = 0.6  # below this, escalate to the next stage / flag for user confirmation

EXTRACTION_SYSTEM_PROMPT = """You are an information-extraction agent for SaveIt, an
opportunity tracker. Given raw text describing a hackathon, internship, scholarship,
fellowship, course, meetup, or government scheme, extract structured data.

Respond ONLY with valid JSON matching this exact shape, nothing else:
{
  "title": string,
  "organization": string or null,
  "category": one of ["hackathon","internship","scholarship","fellowship","course","meetup","government_scheme","other"],
  "deadline": string in ISO 8601 format (YYYY-MM-DD) or null if not found,
  "eligibility": string or null,
  "stipend": string or null,
  "confidence_score": float between 0.0 and 1.0 reflecting how certain you are
    the deadline is correct and complete
}

If the deadline is genuinely absent from the text, set "deadline" to null and
confidence_score low (below 0.5) rather than guessing."""


async def call_llm_extract(raw_text: str) -> dict:
    """Single structured-extraction call to Claude. Returns a parsed dict."""
    if not settings.ANTHROPIC_API_KEY:
        # No key configured — low-confidence stub so the pipeline still runs
        # end-to-end locally without crashing.
        return {
            "title": (raw_text.strip().split("\n")[0][:80] if raw_text.strip() else "Untitled opportunity"),
            "organization": None,
            "category": "other",
            "deadline": None,
            "eligibility": None,
            "stipend": None,
            "confidence_score": 0.0,
        }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.LLM_MODEL,
                "max_tokens": 1024,
                "system": EXTRACTION_SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": raw_text or "No text provided."}],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        text_block = next(
            (b["text"] for b in data.get("content", []) if b.get("type") == "text"), "{}"
        )
        cleaned = re.sub(r"```json|```", "", text_block).strip()
        return json.loads(cleaned)


async def scrape_linked_page(url: str) -> Optional[str]:
    """Stage 2 — fetch and extract visible text from a landing page (Unstop, Google Form, college site)."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "SaveItBot/1.0"})
            resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        return text[:6000]  # cap length fed to the LLM
    except Exception as e:
        print(f"[llm_extract] Stage 2 scrape failed for {url}: {e}")
        return None


def _parse_result(result: dict) -> tuple:
    deadline_dt = None
    if result.get("deadline"):
        try:
            deadline_dt = datetime.fromisoformat(result["deadline"])
        except ValueError:
            pass
    try:
        category = Category(result.get("category", "other"))
    except ValueError:
        category = Category.OTHER
    return deadline_dt, category


async def run_extraction_pipeline(
    raw_text: Optional[str], raw_url: Optional[str]
) -> ExtractionResult:
    """
    Orchestrates all three stages. The reel/message stays the "source of
    discovery"; whichever stage actually resolves the deadline becomes the
    labelled "source of truth" (deadline_source_label).
    """
    stage_used = "media"
    deadline_source_url = raw_url
    deadline_source_label = None

    # Stage 1: whatever text we already have (caption / message / OCR+transcript
    # already concatenated by the caller before this function runs).
    result = await call_llm_extract(raw_text or "")

    # Stage 2: a linked landing page exists and Stage 1 is low-confidence ->
    # scrape it and prefer it as higher-trust.
    if raw_url and result.get("confidence_score", 0.0) < CONFIDENCE_THRESHOLD:
        page_text = await scrape_linked_page(raw_url)
        if page_text:
            page_result = await call_llm_extract(page_text)
            if page_result.get("confidence_score", 0.0) > result.get("confidence_score", 0.0):
                result = page_result
                stage_used = "linked_page"
                deadline_source_url = raw_url
                deadline_source_label = "Deadline confirmed via linked page"

    # Stage 3: still missing/low-confidence -> live web search fallback.
    if result.get("confidence_score", 0.0) < CONFIDENCE_THRESHOLD:
        program_name = result.get("title", "")
        if program_name:
            search_hit = await search_for_deadline(program_name)
            if search_hit and search_hit.get("text"):
                search_result = await call_llm_extract(search_hit["text"])
                if search_result.get("confidence_score", 0.0) > result.get("confidence_score", 0.0):
                    result = search_result
                    stage_used = "web_search_fallback"
                    deadline_source_url = search_hit["url"]
                    deadline_source_label = "Deadline confirmed via official site"

    deadline_dt, category = _parse_result(result)

    return ExtractionResult(
        title=result.get("title") or "Untitled opportunity",
        organization=result.get("organization"),
        category=category,
        deadline=deadline_dt,
        eligibility=result.get("eligibility"),
        stipend=result.get("stipend"),
        confidence_score=float(result.get("confidence_score", 0.0)),
        stage_used=stage_used,
        deadline_source_url=deadline_source_url,
        deadline_source_label=deadline_source_label,
    )
