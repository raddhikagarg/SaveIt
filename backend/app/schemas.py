from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ---------- Enums ----------

class EntryType(str, Enum):
    """Determines whether extracted content goes to the Tracker or the Resources tab."""
    OPPORTUNITY = "opportunity"   # has a deadline -> goes to Tracker
    RESOURCE = "resource"          # no deadline, just useful info -> goes to Resources tab


class Category(str, Enum):
    HACKATHON = "hackathon"
    INTERNSHIP = "internship"
    SCHOLARSHIP = "scholarship"
    FELLOWSHIP = "fellowship"
    COURSE = "course"
    MEETUP = "meetup"
    GOVERNMENT_SCHEME = "government_scheme"
    RESOURCE_LIST = "resource_list"   # e.g. "top 5 websites for X"
    OTHER = "other"


class SourceType(str, Enum):
    INSTAGRAM_REEL = "instagram_reel"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    LINKEDIN = "linkedin"
    ARTICLE_LINK = "article_link"
    UNSTOP = "unstop"
    GOOGLE_LINK = "google_link"
    GOVT_PORTAL = "govt_portal"       # auto-scraped by Govt Radar
    MANUAL = "manual"


# ---------- Extraction pipeline output (internal contract) ----------
# This is the shape the LLM extraction step (Stage 1/2/3) must return.

class ExtractionResult(BaseModel):
    entry_type: EntryType
    title: str
    organization: Optional[str] = None
    category: Category
    deadline: Optional[datetime] = None          # only relevant if entry_type == OPPORTUNITY
    eligibility: Optional[str] = None
    stipend: Optional[str] = None
    source_link: Optional[str] = None
    deadline_source: Optional[str] = None         # "reel" | "linked_page" | "web_search" — Stage 1/2/3 origin
    confidence_score: float = Field(ge=0.0, le=1.0)
    resource_items: Optional[List[str]] = None    # e.g. list of website names/links, only for RESOURCE type


# ---------- Tracker entry (Opportunity) ----------

class TrackerEntryCreate(BaseModel):
    title: str
    organization: Optional[str] = None
    category: Category
    deadline: datetime
    eligibility: Optional[str] = None
    stipend: Optional[str] = None
    source_link: Optional[str] = None
    source_type: SourceType
    confidence_score: float = Field(ge=0.0, le=1.0)
    deadline_source: Optional[str] = None
    user_confirmed: bool = False   # true once user confirms a low-confidence extraction


class TrackerEntryResponse(TrackerEntryCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True   # allows converting from SQLAlchemy models directly


# ---------- Resource entry (no deadline) ----------

class ResourceEntryCreate(BaseModel):
    title: str
    category: Category
    items: List[str]              # e.g. ["Website A - link", "Website B - link"]
    source_link: Optional[str] = None
    source_type: SourceType


class ResourceEntryResponse(ResourceEntryCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = Truegit add .
git status
