"""
Runs background jobs on a schedule — no separate Celery/Redis infrastructure
needed for a hackathon; APScheduler runs in-process alongside FastAPI.
"""
import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import SessionLocal
from app.services.reminder_dispatch import dispatch_due_reminders

logger = logging.getLogger("scheduler")
scheduler = AsyncIOScheduler()


async def _run_reminder_dispatch():
    db = SessionLocal()
    try:
        sent = await dispatch_due_reminders(db)
        if sent:
            logger.info(f"Sent {sent} reminder(s).")
    finally:
        db.close()


def start_scheduler():
    # Every 5 minutes is fine for a demo; every hour is plenty in production.
    scheduler.add_job(_run_reminder_dispatch, "interval", minutes=5, id="reminder_dispatch")
    scheduler.start()
