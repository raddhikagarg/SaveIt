"""
Govt Radar — platform-curated Government of India opportunity feed
(MyBharat, NSP, PM Internship Scheme, etc). This is the "resources" a user
browses without having personally submitted anything, plus the content pool
for inactivity re-engagement nudges.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GovtScheme
from app.schemas import GovtSchemeOut
from app.services.llm_extract import scrape_linked_page, call_llm_extract

router = APIRouter(prefix="/resources", tags=["resources"])

# Listing pages to poll on a schedule (cron / Celery beat). These are entry
# points only — real scrapers should walk pagination and individual listing
# detail pages, which needs per-source maintenance as markup changes.
GOVT_SOURCES = {
    "mybharat": "https://www.mybharat.gov.in/",
    "nsp": "https://scholarships.gov.in/",
    "pminternship": "https://pminternship.mca.gov.in/",
}


@router.get("", response_model=List[GovtSchemeOut])
def list_govt_schemes(
    category: Optional[str] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Browsable curated feed."""
    query = db.query(GovtScheme).filter(GovtScheme.is_active == True)  # noqa: E712
    if category:
        query = query.filter(GovtScheme.category == category)
    if source:
        query = query.filter(GovtScheme.source == source)
    return query.order_by(GovtScheme.deadline.asc().nullslast()).all()


@router.post("/scrape", status_code=202)
async def trigger_scrape(db: Session = Depends(get_db)):
    """
    Admin/demo endpoint to manually trigger a scrape cycle across all
    configured govt sources. In production, call this logic from a
    scheduled job (Celery beat / cron) instead of an exposed endpoint.
    Reuses the same extraction pipeline building blocks as My Tracker.
    """
    scraped_count = 0
    for source_key, url in GOVT_SOURCES.items():
        page_text = await scrape_linked_page(url)
        if not page_text:
            continue

        extracted = await call_llm_extract(page_text)
        if not extracted.get("title"):
            continue

        deadline_dt = None
        if extracted.get("deadline"):
            try:
                deadline_dt = datetime.fromisoformat(extracted["deadline"])
            except ValueError:
                pass

        scheme = GovtScheme(
            title=extracted["title"],
            organization=extracted.get("organization"),
            source=source_key,
            deadline=deadline_dt,
            url=url,
            description=extracted.get("eligibility"),
        )
        db.add(scheme)
        scraped_count += 1

    db.commit()
    return {"schemes_scraped": scraped_count}
