"""
Pydantic schemas for Content endpoints.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class PillarCreate(BaseModel):
    name: str
    description: str | None = None


class PillarResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    is_active: bool
    sort_order: int
    created_at: datetime


class IdeaCreate(BaseModel):
    title: str
    description: str | None = None
    pillar_id: uuid.UUID | None = None
    campaign_id: uuid.UUID | None = None
    topic_id: uuid.UUID | None = None
    audience: str | None = None
    funnel_stage: str | None = None
    suggested_formats: str | None = None
    suggested_platforms: str | None = None
    priority_score: float = 0.0


class IdeaResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    title: str
    description: str | None
    pillar_id: uuid.UUID | None
    campaign_id: uuid.UUID | None
    audience: str | None
    funnel_stage: str | None
    priority_score: float
    status: str
    created_by_agent: bool
    created_at: datetime


class AssetCreate(BaseModel):
    idea_id: uuid.UUID | None = None
    title: str
    body: str
    summary: str | None = None
    language: str = "en"
    medical_risk: str = "low"
    source_citations: str | None = None


class AssetResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    title: str
    body: str
    summary: str | None
    language: str
    medical_risk: str
    status: str
    version: int
    source_citations: str | None
    created_at: datetime
    updated_at: datetime


class VariantCreate(BaseModel):
    platform: str
    format: str
    title: str | None = None
    hook: str | None = None
    body: str
    caption: str | None = None
    cta: str | None = None
    hashtags: str | None = None
    language: str = "en"


class VariantResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    canonical_asset_id: uuid.UUID
    platform: str
    format: str
    title: str | None
    hook: str | None
    body: str
    caption: str | None
    cta: str | None
    hashtags: str | None
    status: str
    language: str
    created_at: datetime


# ── Approval workflow schemas ───────────────────────────────────────────────

class StatusTransitionRequest(BaseModel):
    """Request to transition an asset to a new lifecycle status."""
    status: str
    comment: str | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        from app.models.content import ContentStatus
        valid = {s.value for s in ContentStatus}
        if v not in valid:
            raise ValueError(f"Invalid status '{v}'. Must be one of: {sorted(valid)}")
        return v


class ApprovalRequest(BaseModel):
    """Record an approval decision on a content asset."""
    review_type: str  # fact_check | medical | brand
    decision: str     # approved | rejected | needs_revision
    comments: str | None = None

    @field_validator("review_type")
    @classmethod
    def validate_review_type(cls, v: str) -> str:
        if v not in ("fact_check", "medical", "brand"):
            raise ValueError("review_type must be 'fact_check', 'medical', or 'brand'")
        return v

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v: str) -> str:
        if v not in ("approved", "rejected", "needs_revision"):
            raise ValueError("decision must be 'approved', 'rejected', or 'needs_revision'")
        return v


class ApprovalResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    asset_id: uuid.UUID
    reviewer_id: uuid.UUID | None
    review_type: str
    decision: str
    comments: str | None
    asset_version: int
    is_ai_review: bool
    created_at: datetime


class ClaimResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    asset_id: uuid.UUID
    claim_text: str
    claim_category: str | None
    verification_status: str
    medical_risk: str
    created_at: datetime
