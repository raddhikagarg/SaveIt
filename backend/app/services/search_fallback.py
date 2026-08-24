"""
Stage 3 — live web search fallback.

Triggers only when Stages 1 & 2 leave the deadline missing or
low-confidence. Searches for the extracted program name and returns
the top result's text + URL, so the caller can re-run LLM extraction
on cleaner, higher-trust source text.
"""
from typing import Optional, Dict

import httpx

from app.config import settings


async def search_for_deadline(program_name: str) -> Optional[Dict[str, str]]:
    """
    Search the web for '<program_name> application deadline' via Tavily
    (preferred — returns clean text for LLM agents). Falls back to Serper
    if TAVILY_API_KEY isn't set but SERPER_API_KEY is.
    Returns {"text": ..., "url": ...} for the top result, or None.
    """
    if settings.TAVILY_API_KEY:
        return await _search_tavily(program_name)
    return await _search_serper(program_name)


async def _search_tavily(program_name: str) -> Optional[Dict[str, str]]:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.TAVILY_API_KEY,
                    "query": f"{program_name} application deadline",
                    "max_results": 3,
                },
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
        if not results:
            return None
        top = results[0]
        return {"text": top.get("content", ""), "url": top.get("url", "")}
    except Exception as e:
        print(f"[search_fallback] Tavily search failed: {e}")
        return None


async def _search_serper(program_name: str) -> Optional[Dict[str, str]]:
    import os

    serper_key = os.getenv("SERPER_API_KEY", "")
    if not serper_key:
        return None

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": serper_key, "Content-Type": "application/json"},
                json={"q": f"{program_name} application deadline"},
            )
            resp.raise_for_status()
            organic = resp.json().get("organic", [])
        if not organic:
            return None
        top = organic[0]
        return {"text": top.get("snippet", ""), "url": top.get("link", "")}
    except Exception as e:
        print(f"[search_fallback] Serper search failed: {e}")
        return None
