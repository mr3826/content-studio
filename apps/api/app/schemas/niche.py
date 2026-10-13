from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field




class ContentPillar(BaseModel):
    id: str = Field(..., description="Unique pillar identifier")
    name: str = Field(..., description="Pillar display name")
    description: str = Field(default="", description="Description of covered topics")
    keywords: List[str] = Field(default_factory=list, description="Dedicated matching keywords for this pillar")
    synonyms: List[str] = Field(default_factory=list, description="Alternative names or synonyms")
    examples: List[str] = Field(default_factory=list, description="Representative topic or video examples")


class TopicException(BaseModel):
    topic_or_keyword: str = Field(..., description="Blocked topic or negative keyword subject to exception")
    allowed_contexts: List[str] = Field(
        default_factory=lambda: ["debunking", "criticism", "quotation", "educational"],
        description="Permitted editorial contexts (e.g. debunking, criticism, quotation)"
    )
    notes: Optional[str] = Field(default=None, description="Optional editorial justification")


class NicheProfileBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Niche name")
    one_sentence_definition: str = Field(..., min_length=5, description="Clear one-sentence summary of the niche")
    audience: str = Field(..., min_length=3, description="Target technical audience")
    audience_regions: List[str] = Field(default_factory=list)
    target_skill_levels: List[str] = Field(default_factory=list, description="Target skill levels (e.g. beginner, intermediate, advanced)")
    audience_goals: List[str] = Field(default_factory=list, description="Audience objectives and desired outcomes")
    primary_problems: List[str] = Field(default_factory=list)
    allowed_topics: List[str] = Field(default_factory=list)
    adjacent_topics: List[str] = Field(default_factory=list)
    blocked_topics: List[str] = Field(default_factory=list)
    topic_exceptions: List[TopicException] = Field(default_factory=list, description="Contextual exceptions for sensitive phrases")
    must_have_signals: List[str] = Field(default_factory=list)
    negative_keywords: List[str] = Field(default_factory=list)
    preferred_source_types: List[str] = Field(default_factory=list)
    content_pillars: List[ContentPillar] = Field(default_factory=list)
    commercial_intent_topics: List[str] = Field(default_factory=list)
    evergreen_topics: List[str] = Field(default_factory=list)
    policy_version: int = Field(default=1, description="Policy version revision number")
    policy_fingerprint: Optional[str] = Field(default=None, description="Canonical SHA-256 fingerprint of niche policy")


class NicheProfileCreate(NicheProfileBase):
    pass


class NicheProfileUpdate(NicheProfileBase):
    pass


class NicheProfileRead(NicheProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NichePolicyAuditRead(BaseModel):
    id: str
    niche_id: str
    version: int
    fingerprint: str
    change_summary: str
    snapshot: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NicheDryRunRequest(BaseModel):
    proposed_niche: Optional[NicheProfileBase] = Field(default=None, description="Optional proposed niche profile to test against")
    sample_title: str = Field(..., description="Title of sample item to evaluate")
    sample_text: str = Field(default="", description="Summary, body or context of sample item")
    sample_tags: List[str] = Field(default_factory=list, description="Tags for sample item")


class NicheDryRunResponse(BaseModel):
    verdict: Dict[str, Any] = Field(..., description="Evaluated verdict on sample item")
    policy_version: int = Field(..., description="Version of policy used for evaluation")
    policy_fingerprint: Optional[str] = Field(default=None, description="Fingerprint of policy used")
    is_proposed_preview: bool = Field(default=False, description="Whether evaluation was against a proposed profile preview")
