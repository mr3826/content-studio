from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.engines.niche_guard.contracts import NicheGuardInput
from app.engines.niche_guard.engine import NicheGuardEngine
from app.schemas.niche import (
    NicheDryRunRequest,
    NicheDryRunResponse,
    NichePolicyAuditRead,
    NicheProfileBase,
    NicheProfileRead,
    NicheProfileUpdate,
)
from app.services import niche_service

router = APIRouter(prefix="/niche", tags=["Single Niche"])


@router.get("", response_model=NicheProfileRead)
async def get_active_niche(session: AsyncSession = Depends(get_db)):
    """Fetch the active single niche profile."""
    profile = await niche_service.get_niche_profile(session)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NicheProfile has not been configured yet. Initial setup required.",
        )
    return profile


@router.put("", response_model=NicheProfileRead)
async def update_active_niche(
    payload: NicheProfileUpdate,
    session: AsyncSession = Depends(get_db),
):
    """Save or update the single active niche profile.
    Enforces the single-niche invariant: only one active niche profile exists.
    """
    profile = await niche_service.upsert_niche_profile(session, payload)
    return profile


@router.post("/seed-default", response_model=NicheProfileRead)
async def seed_default_niche(session: AsyncSession = Depends(get_db)):
    """Seed the default niche profile from config/niche.example.yaml."""
    profile = await niche_service.seed_default_niche_if_empty(session)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not seed default niche profile.",
        )
    return profile


@router.get("/policy-audits", response_model=List[NichePolicyAuditRead])
async def get_policy_audits(session: AsyncSession = Depends(get_db)):
    """Fetch history of versioned niche policy audits."""
    return await niche_service.get_niche_policy_audits(session)


@router.post("/dry-run", response_model=NicheDryRunResponse)
async def dry_run_niche_evaluation(
    payload: NicheDryRunRequest,
    session: AsyncSession = Depends(get_db),
):
    """Preview / test how a candidate topic evaluates against the active or a proposed niche policy without persisting changes."""
    engine = NicheGuardEngine()
    is_proposed = payload.proposed_niche is not None

    if is_proposed:
        niche_data = payload.proposed_niche.model_dump()
        version = payload.proposed_niche.policy_version or 1
        fingerprint = niche_service.compute_canonical_niche_fingerprint(niche_data)
    else:
        profile = await niche_service.get_niche_profile(session)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active niche profile not configured. Provide proposed_niche or configure profile first.",
            )
        niche_data = {
            "name": profile.name,
            "one_sentence_definition": profile.one_sentence_definition,
            "audience": profile.audience,
            "target_skill_levels": profile.target_skill_levels or [],
            "audience_goals": profile.audience_goals or [],
            "allowed_topics": profile.allowed_topics or [],
            "adjacent_topics": profile.adjacent_topics or [],
            "blocked_topics": profile.blocked_topics or [],
            "topic_exceptions": profile.topic_exceptions or [],
            "must_have_signals": profile.must_have_signals or [],
            "negative_keywords": profile.negative_keywords or [],
            "content_pillars": profile.content_pillars or [],
            "primary_problems": profile.primary_problems or [],
            "commercial_intent_topics": profile.commercial_intent_topics or [],
            "evergreen_topics": profile.evergreen_topics or [],
            "policy_version": profile.policy_version,
            "policy_fingerprint": profile.policy_fingerprint,
        }
        version = profile.policy_version or 1
        fingerprint = profile.policy_fingerprint

    item = NicheGuardInput(
        id="preview-candidate",
        title=payload.sample_title,
        text=payload.sample_text,
        tags=payload.sample_tags,
    )
    verdict = engine.evaluate_item(item, niche_data)

    return NicheDryRunResponse(
        verdict=verdict.model_dump(mode="json"),
        policy_version=version,
        policy_fingerprint=fingerprint,
        is_proposed_preview=is_proposed,
    )
