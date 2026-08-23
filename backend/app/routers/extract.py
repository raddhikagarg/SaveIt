"""
Entry point for raw content submission — manual paste, or called internally
by routers/webhooks.py for Telegram/Instagram intake. Runs the three-stage
extraction pipeline (services/llm_extract.py, services/search_fallback.py)
and writes a new tracked Opportunity.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Opportunity, OpportunityStatus
from app.schemas import OpportunityOut, OpportunitySubmitRaw
from app.services.llm_extract import run_extraction_pipeline, CONFIDENCE_THRESHOLD
from app.routers.tracker import schedule_reminders_for_opportunity

router = APIRouter(prefix="/extract", tags=["extract"])


@router.post("/submit", response_model=OpportunityOut)
async def submit_raw_content(payload: OpportunitySubmitRaw, db: Session = Depends(get_db)):
    """
    Runs raw text/URL through the three-stage extraction pipeline and creates
    a tracked opportunity. Low-confidence extractions are flagged for a
    one-tap user confirmation instead of being silently trusted.
    """
    result = await run_extraction_pipeline(payload.raw_text, payload.raw_url)

    status = (
        OpportunityStatus.ACTIVE
        if result.confidence_score >= CONFIDENCE_THRESHOLD
        else OpportunityStatus.NEEDS_CONFIRMATION
    )

    opportunity = Opportunity(
        user_id=payload.user_id,
        title=result.title,
        organization=result.organization,
        category=result.category,
        deadline=result.deadline,
        eligibility=result.eligibility,
        stipend=result.stipend,
        source_type=payload.source_type,
        raw_source_url=payload.raw_url,
        deadline_source_url=result.deadline_source_url,
        deadline_source_label=result.deadline_source_label,
        confidence_score=result.confidence_score,
        extraction_stage=result.stage_used,
        status=status,
    )
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)

    if opportunity.deadline and status == OpportunityStatus.ACTIVE:
        schedule_reminders_for_opportunity(db, opportunity)

    return opportunity
