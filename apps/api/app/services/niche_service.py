import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid
import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.niche import NichePolicyAudit, NicheProfile, SINGLETON_NICHE_ID
from app.schemas.niche import NicheProfileBase, NicheProfileCreate, NicheProfileUpdate


def compute_canonical_niche_fingerprint(data: Dict[str, Any]) -> str:
    """Deterministically compute SHA-256 fingerprint for material niche policy definition.
    Ignores non-semantic metadata such as IDs and timestamps.
    """
    def _normalize(val: Any) -> Any:
        if isinstance(val, list):
            # If list of dicts, sort by JSON representation
            if val and isinstance(val[0], dict):
                return sorted([_normalize(item) for item in val], key=lambda x: json.dumps(x, sort_keys=True))
            return sorted([str(x).strip().lower() for x in val if x])
        if isinstance(val, dict):
            return {k: _normalize(v) for k, v in sorted(val.items()) if k not in ("id", "created_at", "updated_at")}
        if isinstance(val, str):
            return val.strip().lower()
        return val

    canonical_data = {
        "name": _normalize(data.get("name", "")),
        "one_sentence_definition": _normalize(data.get("one_sentence_definition", "")),
        "audience": _normalize(data.get("audience", "")),
        "target_skill_levels": _normalize(data.get("target_skill_levels", [])),
        "audience_goals": _normalize(data.get("audience_goals", [])),
        "primary_problems": _normalize(data.get("primary_problems", [])),
        "allowed_topics": _normalize(data.get("allowed_topics", [])),
        "adjacent_topics": _normalize(data.get("adjacent_topics", [])),
        "blocked_topics": _normalize(data.get("blocked_topics", [])),
        "topic_exceptions": _normalize(data.get("topic_exceptions", [])),
        "must_have_signals": _normalize(data.get("must_have_signals", [])),
        "negative_keywords": _normalize(data.get("negative_keywords", [])),
        "content_pillars": _normalize(data.get("content_pillars", [])),
        "commercial_intent_topics": _normalize(data.get("commercial_intent_topics", [])),
        "evergreen_topics": _normalize(data.get("evergreen_topics", [])),
    }

    serialized = json.dumps(canonical_data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


async def get_niche_profile(session: AsyncSession) -> Optional[NicheProfile]:
    stmt = select(NicheProfile).where(NicheProfile.id == SINGLETON_NICHE_ID)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def upsert_niche_profile(
    session: AsyncSession, data: NicheProfileBase
) -> NicheProfile:
    """Save or update the single niche profile.
    Enforces the single-niche invariant: exactly one primary profile.
    Computes canonical policy fingerprint and tracks policy version revisions.
    """
    profile = await get_niche_profile(session)
    data_dict = data.model_dump()

    # Convert content_pillars models to dict if needed
    if "content_pillars" in data_dict and data_dict["content_pillars"]:
        data_dict["content_pillars"] = [
            p.model_dump() if hasattr(p, "model_dump") else p
            for p in data.content_pillars
        ]

    # Convert topic_exceptions models to dict if needed
    if "topic_exceptions" in data_dict and data_dict["topic_exceptions"]:
        data_dict["topic_exceptions"] = [
            te.model_dump() if hasattr(te, "model_dump") else te
            for te in data.topic_exceptions
        ]

    # Compute policy fingerprint
    fingerprint = compute_canonical_niche_fingerprint(data_dict)
    data_dict["policy_fingerprint"] = fingerprint

    if profile is None:
        data_dict["policy_version"] = 1
        profile = NicheProfile(id=SINGLETON_NICHE_ID, **data_dict)
        session.add(profile)

        # Record initial policy audit
        audit = NichePolicyAudit(
            id=str(uuid.uuid4()),
            niche_id=SINGLETON_NICHE_ID,
            version=1,
            fingerprint=fingerprint,
            change_summary=f"Initial niche policy v1 configured: '{data.name}'",
            snapshot=data_dict,
        )
        session.add(audit)
    else:
        # Check if material policy rules changed
        old_fingerprint = profile.policy_fingerprint
        if old_fingerprint and old_fingerprint == fingerprint:
            # Semantically identical: keep current policy version
            data_dict["policy_version"] = profile.policy_version or 1
        else:
            # Material change: increment policy version and create audit snapshot
            new_version = (profile.policy_version or 1) + 1
            data_dict["policy_version"] = new_version

            audit = NichePolicyAudit(
                id=str(uuid.uuid4()),
                niche_id=SINGLETON_NICHE_ID,
                version=new_version,
                fingerprint=fingerprint,
                change_summary=f"Material policy revision v{new_version}: updated taxonomy rules",
                snapshot=data_dict,
            )
            session.add(audit)

        for k, v in data_dict.items():
            setattr(profile, k, v)

    await session.commit()
    await session.refresh(profile)
    return profile


async def get_niche_policy_audits(session: AsyncSession) -> List[NichePolicyAudit]:
    """Fetch history of versioned niche policy changes."""
    stmt = (
        select(NichePolicyAudit)
        .where(NichePolicyAudit.niche_id == SINGLETON_NICHE_ID)
        .order_by(NichePolicyAudit.version.desc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def seed_default_niche_if_empty(session: AsyncSession) -> Optional[NicheProfile]:
    existing = await get_niche_profile(session)
    if existing:
        return existing

    example_path = Path("config/niche.example.yaml")
    if example_path.exists():
        with open(example_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
            # Remove id if present so schema parses cleanly
            raw.pop("id", None)
            base = NicheProfileBase(**raw)
            return await upsert_niche_profile(session, base)
    return None
