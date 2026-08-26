"""
Checks for due reminders and sends them. Called on a schedule (see scheduler.py),
not triggered by any user action — this is what actually closes the loop on
'never miss a deadline', since schedule_reminders_for_opportunity() only
creates the Reminder rows; this is what fires them.
"""
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Reminder, Opportunity, User
from app.services.notifications import notify_user


async def dispatch_due_reminders(db: Session) -> int:
    due_reminders = (
        db.query(Reminder)
        .filter(Reminder.sent == False, Reminder.remind_at <= datetime.utcnow())
        .all()
    )

    sent_count = 0
    for reminder in due_reminders:
        opportunity = db.query(Opportunity).filter(Opportunity.id == reminder.opportunity_id).first()
        if not opportunity:
            reminder.sent = True  # orphaned reminder, mark done so it stops being picked up
            continue

        user = db.query(User).filter(User.id == opportunity.user_id).first()
        if not user:
            reminder.sent = True
            continue

        deadline_str = opportunity.deadline.strftime("%b %d") if opportunity.deadline else "soon"
        message = (
            f"\u23f0 Reminder: \"{opportunity.title}\""
            f"{' at ' + opportunity.organization if opportunity.organization else ''} "
            f"closes on {deadline_str} ({reminder.days_before_deadline} day(s) left).\n"
            f"{opportunity.raw_source_url or ''}"
        )

        success = await notify_user(user, message)
        if success:
            reminder.sent = True
            reminder.sent_at = datetime.utcnow()
            sent_count += 1

    db.commit()
    return sent_count
