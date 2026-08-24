"""
Intake webhooks — Telegram (primary demo channel, no review process) and
Instagram Business Messaging API (secondary channel, requires Meta app review).
Both call routers/extract.py's pipeline entry point after resolving/creating a user.
"""
import httpx
from fastapi import APIRouter, Depends, Request, Query, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User, OpportunityStatus, SourceType
from app.schemas import OpportunitySubmitRaw
from app.routers.extract import submit_raw_content

router = APIRouter(prefix="/webhook", tags=["webhooks"])


# ---------- Telegram ----------

def _get_or_create_telegram_user(db: Session, chat_id: str) -> User:
    user = db.query(User).filter(User.telegram_chat_id == chat_id).first()
    if not user:
        user = User(telegram_chat_id=chat_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


async def _send_telegram_message(chat_id: str, text: str) -> None:
    if not settings.TELEGRAM_BOT_TOKEN:
        print(f"[telegram stub] -> {chat_id}: {text}")
        return
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text},
        )


@router.post("/telegram")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Set the webhook once with:
    https://api.telegram.org/bot<TOKEN>/setWebhook?url=<YOUR_HTTPS_URL>/webhook/telegram
    """
    payload = await request.json()
    message = payload.get("message", {})
    chat_id = str(message.get("chat", {}).get("id", ""))
    text = message.get("text", "") or message.get("caption", "")

    if not chat_id or not text:
        return {"ok": True}  # ignore non-text updates for MVP (stickers, etc.)

    user = _get_or_create_telegram_user(db, chat_id)

    raw_url = text.strip() if text.strip().startswith("http") else None
    raw_text = None if raw_url else text

    opportunity = await submit_raw_content(
        OpportunitySubmitRaw(
            user_id=user.id,
            source_type=SourceType.TELEGRAM,
            raw_text=raw_text,
            raw_url=raw_url,
        ),
        db,
    )

    if opportunity.status == OpportunityStatus.NEEDS_CONFIRMATION:
        reply = (
            f"Found: {opportunity.title} — but I couldn't confirm the deadline confidently. "
            f"Tap to confirm in your tracker."
        )
    else:
        deadline_str = opportunity.deadline.strftime("%b %d") if opportunity.deadline else "TBD"
        reply = f"Added: {opportunity.title}, deadline {deadline_str} \u2705"

    await _send_telegram_message(chat_id, reply)
    return {"ok": True}


# ---------- Instagram ----------

@router.get("/instagram")
def verify_instagram_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    """Meta's webhook verification handshake — required before it will send events."""
    if hub_mode == "subscribe" and hub_verify_token == settings.INSTAGRAM_VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/instagram")
async def instagram_webhook(request: Request, db: Session = Depends(get_db)):
    """Receives a shared reel/DM via the Instagram Messaging API."""
    payload = await request.json()

    for entry in payload.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event.get("sender", {}).get("id")
            message = event.get("message", {})
            text = message.get("text", "")
            attachments = message.get("attachments", [])
            raw_url = attachments[0]["payload"]["url"] if attachments else None

            if not sender_id or (not text and not raw_url):
                continue

            user = db.query(User).filter(User.instagram_scoped_id == sender_id).first()
            if not user:
                user = User(instagram_scoped_id=sender_id)
                db.add(user)
                db.commit()
                db.refresh(user)

            await submit_raw_content(
                OpportunitySubmitRaw(
                    user_id=user.id,
                    source_type=SourceType.INSTAGRAM,
                    raw_text=text or None,
                    raw_url=raw_url,
                ),
                db,
            )

    return {"ok": True}
