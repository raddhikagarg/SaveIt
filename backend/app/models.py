"""
SQLAlchemy ORM models for SaveIt.

Two core domains:
- My Tracker: user-submitted opportunities (Opportunity, Tag, User)
- Govt Radar: platform-curated government opportunities (GovtScheme)
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, DateTime, Float, Boolean, ForeignKey, Enum, Table, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Category(str, enum.Enum):
    HACKATHON = "hackathon"
    INTERNSHIP = "internship"
    SCHOLARSHIP = "scholarship"
    FELLOWSHIP = "fellowship"
    COURSE = "course"
    MEETUP = "meetup"
    GOVERNMENT_SCHEME = "government_scheme"
    OTHER = "other"


class SourceType(str, enum.Enum):
    INSTAGRAM = "instagram"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    LINKEDIN = "linkedin"
    LINK = "link"
    MANUAL = "manual"


class OpportunityStatus(str, enum.Enum):
    NEEDS_CONFIRMATION = "needs_confirmation"  # low-confidence extraction, awaiting user tap
    ACTIVE = "active"
    EXPIRED = "expired"
    ARCHIVED = "archived"


# Many-to-many: opportunities <-> free-form user tags (e.g. "AI-only", "team of 4")
opportunity_tags = Table(
    "opportunity_tags",
    Base.metadata,
    Column("opportunity_id", String, ForeignKey("opportunities.id"), primary_key=True),
    Column("tag_id", String, ForeignKey("tags.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    telegram_chat_id = Column(String, unique=True, nullable=True, index=True)
    instagram_scoped_id = Column(String, unique=True, nullable=True, index=True)
    email = Column(String, unique=True, nullable=True, index=True)

    # Google Calendar sync (calendar.events scope only, secondary calendar)
    google_calendar_connected = Column(Boolean, default=False)
    google_refresh_token = Column(String, nullable=True)
    google_calendar_id = Column(String, nullable=True)  # dedicated "My Opportunities" calendar

      # Login identity (email + password)
    password_hash = Column(String, nullable=True)
    name = Column(String, nullable=True)

    # Additional platform link
    whatsapp_number = Column(String, unique=True, nullable=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)

    opportunities = relationship("Opportunity", back_populates="user", cascade="all, delete-orphan")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, nullable=False, index=True)

    opportunities = relationship("Opportunity", secondary=opportunity_tags, back_populates="tags")


class Opportunity(Base):
    """A single tracked item in 'My Tracker' — the source-agnostic personal module."""
    __tablename__ = "opportunities"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    title = Column(String, nullable=False)
    organization = Column(String, nullable=True)
    category = Column(Enum(Category), default=Category.OTHER, nullable=False)

    deadline = Column(DateTime, nullable=True)
    eligibility = Column(Text, nullable=True)
    stipend = Column(String, nullable=True)

    # Provenance
    source_type = Column(Enum(SourceType), nullable=False)
    raw_source_url = Column(String, nullable=True)      # the reel/message/link the user shared
    deadline_source_url = Column(String, nullable=True)  # where the deadline was actually confirmed
    deadline_source_label = Column(String, nullable=True)  # e.g. "Deadline confirmed via official site"

    # Extraction pipeline metadata
    confidence_score = Column(Float, default=0.0)  # 0.0-1.0
    extraction_stage = Column(String, nullable=True)  # "media" | "linked_page" | "web_search_fallback"
    status = Column(Enum(OpportunityStatus), default=OpportunityStatus.NEEDS_CONFIRMATION)

    # Google Calendar sync
    google_calendar_event_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="opportunities")
    tags = relationship("Tag", secondary=opportunity_tags, back_populates="opportunities")
    reminders = relationship("Reminder", back_populates="opportunity", cascade="all, delete-orphan")


class Reminder(Base):
    """In-app reminder — the always-on source of truth, independent of Google Calendar."""
    __tablename__ = "reminders"

    id = Column(String, primary_key=True, default=gen_uuid)
    opportunity_id = Column(String, ForeignKey("opportunities.id"), nullable=False, index=True)

    remind_at = Column(DateTime, nullable=False)
    days_before_deadline = Column(String, nullable=False)  # "3" or "1"
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)

    opportunity = relationship("Opportunity", back_populates="reminders")


class GovtScheme(Base):
    """A single scraped/curated entry in the platform-wide 'Govt Radar' feed."""
    __tablename__ = "govt_schemes"

    id = Column(String, primary_key=True, default=gen_uuid)

    title = Column(String, nullable=False)
    organization = Column(String, nullable=True)
    source = Column(String, nullable=False)  # "mybharat" | "nsp" | "pminternship" | etc.
    category = Column(Enum(Category), default=Category.GOVERNMENT_SCHEME)

    deadline = Column(DateTime, nullable=True)
    url = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    scraped_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class LinkCode(Base):
    """Short-lived code a logged-in web user sends to Telegram/Instagram/WhatsApp
    to link that platform account to their web account."""
    __tablename__ = "link_codes"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    platform = Column(Enum(SourceType), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
