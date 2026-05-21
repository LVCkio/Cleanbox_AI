"""
CleanInbox AI — SQLAlchemy Models (ORM)
Tương thích cả SQLite (dev) và PostgreSQL (prod).
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, Integer, Float,
    DateTime, Date, ForeignKey, Text, CheckConstraint
)
from sqlalchemy.orm import relationship
from backend.database import Base
import enum


# ─── Helper: UUID column tương thích SQLite + PostgreSQL ────
def UUIDColumn(**kwargs):
    """Dùng String(36) để tương thích cả SQLite và PostgreSQL."""
    return Column(String(36), default=lambda: str(uuid.uuid4()), **kwargs)


# ─── Enums (dùng String thay vì SAEnum để tương thích SQLite) ──
class PlanEnum(str, enum.Enum):
    starter = "starter"
    pro = "pro"
    enterprise = "enterprise"

class ProviderEnum(str, enum.Enum):
    mailchimp = "mailchimp"
    hubspot = "hubspot"
    sendgrid = "sendgrid"

class ConsentEnum(str, enum.Enum):
    active = "active"
    snoozed = "snoozed"
    unsubscribed = "unsubscribed"

class RiskLevelEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


# ─── 1. Organizations ───────────────────────────────
class Organization(Base):
    __tablename__ = "organizations"

    id         = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name       = Column(String(255), nullable=False)
    email      = Column(String(255), unique=True, nullable=False)
    plan       = Column(String(20), default="starter")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    api_connections = relationship("ApiConnection", back_populates="organization", cascade="all, delete")
    contacts        = relationship("Contact", back_populates="organization", cascade="all, delete")
    campaigns       = relationship("Campaign", back_populates="organization", cascade="all, delete")


# ─── 2. API Connections ─────────────────────────────
class ApiConnection(Base):
    __tablename__ = "api_connections"

    id             = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id         = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"))
    provider       = Column(String(20), nullable=False)   # mailchimp | hubspot | sendgrid
    api_key_hash   = Column(Text, nullable=False)          # SHA-256 hash
    access_token   = Column(Text)                          # AES-256 encrypted
    status         = Column(String(20), default="active")
    last_synced_at = Column(DateTime)
    created_at     = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="api_connections")


# ─── 3. Contacts ────────────────────────────────────
class Contact(Base):
    __tablename__ = "contacts"

    id                          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id                      = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"))
    email                       = Column(String(255), nullable=False)
    consent_status              = Column(String(20), default="active")
    consent_given_at            = Column(DateTime)
    snooze_until                = Column(DateTime)
    snooze_days                 = Column(Integer)
    total_emails_received       = Column(Integer, default=0)
    total_emails_opened         = Column(Integer, default=0)
    total_emails_deleted_unread = Column(Integer, default=0)
    ethical_ux_flag             = Column(Boolean, default=False)
    created_at                  = Column(DateTime, default=datetime.utcnow)
    updated_at                  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization    = relationship("Organization", back_populates="contacts")
    micro_behaviors = relationship("MicroBehavior", back_populates="contact", cascade="all, delete")
    fatigue_scores  = relationship("BrandFatigueScore", back_populates="contact", cascade="all, delete")


# ─── 4. Micro Behaviors ─────────────────────────────
class MicroBehavior(Base):
    __tablename__ = "micro_behaviors"

    id                   = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contact_id           = Column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"))
    campaign_id          = Column(String(36), ForeignKey("campaigns.id"), nullable=True)
    event_type           = Column(String(50))
    time_spent_seconds   = Column(Integer, default=0)
    scroll_depth_percent = Column(Float)
    device_type          = Column(String(30))
    recorded_at          = Column(DateTime, default=datetime.utcnow)

    contact = relationship("Contact", back_populates="micro_behaviors")


# ─── 5. Brand Fatigue Scores ────────────────────────
class BrandFatigueScore(Base):
    __tablename__ = "brand_fatigue_scores"

    id                  = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contact_id          = Column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"))
    org_id              = Column(String(36), ForeignKey("organizations.id"))
    bfs_score           = Column(Float, nullable=False)
    score_time_spent    = Column(Float)
    score_delete_unread = Column(Float)
    score_frequency     = Column(Float)
    risk_level          = Column(String(20))
    action_triggered    = Column(String(50))
    calculated_at       = Column(DateTime, default=datetime.utcnow)

    contact = relationship("Contact", back_populates="fatigue_scores")


# ─── 6. Campaigns ───────────────────────────────────
class Campaign(Base):
    __tablename__ = "campaigns"

    id              = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id          = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"))
    name            = Column(String(255))
    provider        = Column(String(20))
    provider_ref_id = Column(String(255))
    sent_at         = Column(DateTime)
    total_sent      = Column(Integer, default=0)
    total_filtered  = Column(Integer, default=0)
    status          = Column(String(30), default="draft")

    organization  = relationship("Organization", back_populates="campaigns")
    esg_tracking  = relationship("EsgCo2Tracking", back_populates="campaign", cascade="all, delete")


# ─── 7. ESG CO2 Tracking ────────────────────────────
class EsgCo2Tracking(Base):
    __tablename__ = "esg_co2_tracking"

    id               = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id           = Column(String(36), ForeignKey("organizations.id"))
    campaign_id      = Column(String(36), ForeignKey("campaigns.id"))
    emails_filtered  = Column(Integer, nullable=False, default=0)
    co2_saved_grams  = Column(Float)
    cost_saved_usd   = Column(Float)
    period_start     = Column(Date)
    period_end       = Column(Date)
    created_at       = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="esg_tracking")
