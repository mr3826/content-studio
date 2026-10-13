from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin

SINGLETON_NICHE_ID = "primary"


class NicheProfile(Base, TimestampMixin):
    """Single Niche Profile (Singleton).
    The studio allows exactly ONE active niche. Multi-tenant workspace switching is forbidden.
    """
    __tablename__ = "niche_profiles"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=SINGLETON_NICHE_ID)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    one_sentence_definition: Mapped[str] = mapped_column(Text, nullable=False)
    audience: Mapped[str] = mapped_column(Text, nullable=False)
    audience_regions: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    target_skill_levels: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    audience_goals: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    primary_problems: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    allowed_topics: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    adjacent_topics: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    blocked_topics: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    topic_exceptions: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    must_have_signals: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    negative_keywords: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_source_types: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    content_pillars: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    commercial_intent_topics: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    evergreen_topics: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    policy_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    policy_fingerprint: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


class NichePolicyAudit(Base, TimestampMixin):
    """Audit log of versioned niche policy changes."""
    __tablename__ = "niche_policy_audits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    niche_id: Mapped[str] = mapped_column(String(32), default=SINGLETON_NICHE_ID, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    change_summary: Mapped[str] = mapped_column(Text, nullable=False)
    snapshot: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
