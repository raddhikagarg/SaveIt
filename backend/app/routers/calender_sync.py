"""
Google Calendar sync — runs in PARALLEL with the in-app reminder engine,
never as a replacement for it. Uses calendar.events scope ONLY (never the
broader calendar-management scope), and only ever calls the insert endpoint
— list/read is never called, so no existing calendar data is touched even
though the scope would technically permit it. Events go to a dedicated
secondary calendar ("My Opportunities"), not the user's primary calendar.
"""
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User, Opportunity

router = APIRouter(prefix="/calendar", tags=["calendar-sync"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
CALENDAR_API_BASE = "https://www.googleapis.com/calendar/v3"

# Narrow scope only — view/edit events, not full calendar management.
SCOPES = "https://www.googleapis.com/auth/calendar.events"


@router.get("/connect")
def start_google_oauth(user_id: str):
    """Redirect target: send the user's browser to Google's consent screen."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "state": user_id,  # round-trip the user id through the OAuth flow
    }
    return {"auth_url": f"{GOOGLE_AUTH_URL}?{urlencode(params)}"}


@router.get("/callback")
async def google_oauth_callback(
    code: str = Query(...), state: str = Query(...), db: Session = Depends(get_db)
):
    """Google redirects here after consent. Exchanges the code for tokens,
    creates the dedicated 'My Opportunities' calendar, and stores the refresh token."""
    user = db.query(User).filter(User.id == state).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    async with httpx.AsyncClient(timeout=15) as client:
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        token_resp.raise_for_status()
        tokens = token_resp.json()

    refresh_token = tokens.get("refresh_token")
    access_token = tokens["access_token"]

    # Create (or reuse) the dedicated secondary calendar.
    async with httpx.AsyncClient(timeout=15) as client:
        cal_resp = await client.post(
            f"{CALENDAR_API_BASE}/calendars",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"summary": "My Opportunities"},
        )
        cal_resp.raise_for_status()
        calendar_id = cal_resp.json()["id"]

    user.google_calendar_connected = True
    user.google_refresh_token = refresh_token
    user.google_calendar_id = calendar_id
    db.commit()

    return {"connected": True, "calendar_id": calendar_id}


async def _get_access_token(refresh_token: str) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "refresh_token": refresh_token,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "grant_type": "refresh_token",
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


@router.post("/sync/{opportunity_id}")
async def sync_opportunity_to_calendar(opportunity_id: str, db: Session = Depends(get_db)):
    """
    Write-only insert of one opportunity's deadline as a calendar event.
    Call this after an opportunity is created/updated with a deadline —
    it's additive to the in-app reminder, never a dependency for it.
    """
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    if not opportunity.deadline:
        raise HTTPException(status_code=400, detail="Opportunity has no deadline to sync")

    user = db.query(User).filter(User.id == opportunity.user_id).first()
    if not user or not user.google_calendar_connected or not user.google_refresh_token:
        raise HTTPException(status_code=400, detail="User has not connected Google Calendar")

    access_token = await _get_access_token(user.google_refresh_token)
    deadline_str = opportunity.deadline.strftime("%Y-%m-%d")

    event_body = {
        "summary": f"Deadline: {opportunity.title}",
        "description": (
            f"Organization: {opportunity.organization or 'N/A'}\n"
            f"Source: {opportunity.raw_source_url or 'manual entry'}\n"
            f"Tracked via SaveIt"
        ),
        "start": {"date": deadline_str},
        "end": {"date": deadline_str},
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{CALENDAR_API_BASE}/calendars/{user.google_calendar_id}/events",
            headers={"Authorization": f"Bearer {access_token}"},
            json=event_body,
        )
        resp.raise_for_status()
        event = resp.json()

    opportunity.google_calendar_event_id = event["id"]
    db.commit()

    return {"synced": True, "event_id": event["id"]}
