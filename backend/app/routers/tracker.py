"""
My Tracker — user-submitted, source-agnostic opportunity CRUD + dashboard listing.

Raw-content submission (which triggers the extraction pipeline) lives in
routers/extract.py — this file is for managing opportunities that already exist.
"""
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Opportunity, OpportunityStatus, Tag, Reminder
from app.schemas import OpportunityOut, OpportunityCreate, OpportunityUpdate

router = APIRouter(prefix="/tracker", tags=["tracker"])


def schedule_reminders_for_opportunity(db: Session, opportunity: Opportunity) -> List[Reminder]:
    """Create T-3-day and T-1-day in-app reminders for an opportunity's deadline.
    Always runs unconditionally — the in-app tracker is the source of truth
    regardless of whether Google Calendar is connected."""
    if not opportunity.deadline:
        return []

    created = []
    for days_before in settings.REMINDER_DAYS_BEFORE:
        remind_at = opportunity.deadline - timedelta(days=days_before)
        if remind_at < datetime.utcnow():
            continue
        reminder = Reminder(
            opportunity_id=opportunity.id,
            remind_at=remind_at,
            days_before_deadline=str(days_before),
        )
        db.add(reminder)
        created.append(reminder)

    db.commit()
    for r in created:
        db.refresh(r)
    return created


@router.post("", response_model=OpportunityOut)
def create_opportunity_manual(
    user_id: str, payload: OpportunityCreate, db: Session = Depends(get_db)
):
    """Manual creation path — user fills the form directly instead of sharing raw content."""
    opportunity = Opportunity(
        user_id=user_id,
        title=payload.title,
        organization=payload.organization,
        category=payload.category,
        deadline=payload.deadline,
        eligibility=payload.eligibility,
        stipend=payload.stipend,
        source_type=payload.source_type,
        raw_source_url=payload.raw_source_url,
        confidence_score=1.0,  # user-entered data is trusted
        status=OpportunityStatus.ACTIVE,
    )

    for tag_name in payload.tags:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
        opportunity.tags.append(tag)

    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)

    if opportunity.deadline:
        schedule_reminders_for_opportunity(db, opportunity)

    return opportunity


@router.get("", response_model=List[OpportunityOut])
def list_opportunities(
    user_id: str,
    category: Optional[str] = None,
    status: Optional[str] = None,
    sort_by_deadline: bool = True,
    db: Session = Depends(get_db),
):
    """Dashboard listing with category filter, status filter, and deadline sort."""
    query = db.query(Opportunity).filter(Opportunity.user_id == user_id)
    if category:
        query = query.filter(Opportunity.category == category)
    if status:
        query = query.filter(Opportunity.status == status)
    if sort_by_deadline:
        query = query.order_by(Opportunity.deadline.asc().nullslast())
    return query.all()


@router.get("/{opportunity_id}", response_model=OpportunityOut)
def get_opportunity(opportunity_id: str, db: Session = Depends(get_db)):
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity


@router.patch("/{opportunity_id}", response_model=OpportunityOut)
def update_opportunity(
    opportunity_id: str, payload: OpportunityUpdate, db: Session = Depends(get_db)
):
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    update_data = payload.model_dump(exclude_unset=True)
    deadline_changed = "deadline" in update_data and update_data["deadline"] != opportunity.deadline

    for field, value in update_data.items():
        setattr(opportunity, field, value)

    db.commit()
    db.refresh(opportunity)

    if deadline_changed and opportunity.deadline:
        schedule_reminders_for_opportunity(db, opportunity)

    return opportunity


@router.post("/{opportunity_id}/confirm", response_model=OpportunityOut)
def confirm_low_confidence_extraction(opportunity_id: str, db: Session = Depends(get_db)):
    """One-tap confirmation for a low-confidence extraction — flips status to ACTIVE."""
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    opportunity.status = OpportunityStatus.ACTIVE
    db.commit()
    db.refresh(opportunity)

    if opportunity.deadline:
        schedule_reminders_for_opportunity(db, opportunity)

    return opportunity


@router.delete("/{opportunity_id}", status_code=204)
def delete_opportunity(opportunity_id: str, db: Session = Depends(get_db)):
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    db.delete(opportunity)
    db.commit()
