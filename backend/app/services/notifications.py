"""
Actual notification sending — Telegram (if linked) as primary channel,
since it's free, instant, and most of your test users will have it linked.
Email is a documented fallback for later; not required for MVP demo.
"""
import httpx

from app.config import settings
from app.models import User


async def send_telegram_message(chat_id: str, text: str) -> bool:
    if not settings.TELEGRAM_BOT_TOKEN or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json={"chat_id": chat_id, "text": text})
            return resp.status_code == 200
    except httpx.HTTPError:
        return False


async def notify_user(user: User, message: str) -> bool:
    """
    Tries each linked channel in order of reliability/speed.
    Returns True if at least one channel succeeded.
    Extend this with email/WhatsApp sending later — same pattern.
    """
    if user.telegram_chat_id:
        return await send_telegram_message(user.telegram_chat_id, message)

    # TODO: WhatsApp via Twilio, email via SMTP — add here when needed.
    return False
