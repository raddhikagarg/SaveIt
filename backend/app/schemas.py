"""
Pydantic schemas — request/response shapes for the API.
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict

from app.models import Category, SourceType, OpportunityStatus


# ---------- Shared / small pieces ----------

class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str


# ---------- User ----------

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    telegram_chat_id: Optional[str] = None
    email: Optional[str] = None
    google_calendar_connected: bool
    created_at: datetime


# ---------- Opportunity (My Tracker) ----------

class OpportunityBase(BaseModel):
    title: str
    organization: Optional[str] = None
    category: Category = Category.OTHER
    deadline: Optional[datetime] = None
    eligibility: Optional[str] = None
    stipend: Optional[str] = None


class OpportunityCreate(OpportunityBase):
    """Manual-paste creation path — used when a user pastes a link/text directly."""
    source_type: SourceType = SourceType.MANUAL
    raw_source_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class OpportunitySubmitRaw(BaseModel):
    """Raw content submission — triggers the three-stage extraction pipeline."""
    user_id: str
    source_type: SourceType
    raw_text: Optional[str] = None       # caption / message text / pasted article text
    raw_url: Optional[str] = None        # reel link, landing page link, etc.


class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    organization: Optional[str] = None
    category: Optional[Category] = None
    deadline: Optional[datetime] = None
    eligibility: Optional[str] = None
    stipend: Optional[str] = None
    status: Optional[OpportunityStatus] = None


class OpportunityOut(OpportunityBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    source_type: SourceType
    raw_source_url: Optional[str] = None
    deadline_source_url: Optional[str] = None
    deadline_source_label: Optional[str] = None
    confidence_score: float
    extraction_stage: Optional[str] = None
    status: OpportunityStatus
    google_calendar_event_id: Optional[str] = None
    created_at: datetime
    tags: List[TagOut] = Field(default_factory=list)


# ---------- Extraction pipeline (internal + response shape) ----------

class ExtractionResult(BaseModel):
    """What the three-stage extraction pipeline produces before it's written to the DB."""
    title: str
    organization: Optional[str] = None
    category: Category = Category.OTHER
    deadline: Optional[datetime] = None
    eligibility: Optional[str] = None
    stipend: Optional[str] = None
    confidence_score: float = 0.0
    stage_used: str = "media"  # "media" | "linked_page" | "web_search_fallback"
    deadline_source_url: Optional[str] = None
    deadline_source_label: Optional[str] = None


# ---------- Govt Radar ----------

class GovtSchemeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    organization: Optional[str] = None
    source: str
    category: Category
    deadline: Optional[datetime] = None
    url: str
    description: Optional[str] = None
    scraped_at: datetime


# ---------- Reminders ----------

class ReminderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    opportunity_id: str
    remind_at: datetime
    days_before_deadline: str
    sent: bool


# ---------- Auth ----------

class GoogleLoginRequest(BaseModel):
    id_token: str  # from Google Identity Services on the frontend


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class LinkCodeGenerateRequest(BaseModel):
    platform: SourceType


class LinkCodeOut(BaseModel):
    code: str
    platform: SourceType
    expires_at: datetime
    instructions: str
