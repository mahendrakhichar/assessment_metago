"""
Content Models — Pillars, campaigns, ideas, canonical assets, variants, approval.
"""
import uuid
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class ContentStatus(str, PyEnum):
    DRAFT = "draft"
    FACT_CHECK = "fact_check"
    MEDICAL_REVIEW = "medical_review"
    BRAND_REVIEW = "brand_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    BLOCKED = "blocked"
    REVISION_REQUESTED = "revision_requested"
    ARCHIVED = "archived"


class MedicalRiskLevel(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContentFormat(str, PyEnum):
    YOUTUBE_LONG = "youtube_long"
    YOUTUBE_SHORT = "youtube_short"
    INSTAGRAM_REEL = "instagram_reel"
    INSTAGRAM_CAROUSEL = "instagram_carousel"
    INSTAGRAM_POST = "instagram_post"
    INSTAGRAM_STORY = "instagram_story"
    X_POST = "x_post"
    X_THREAD = "x_thread"
    ARTICLE = "article"
    FAQ = "faq"
    NEWSLETTER = "newsletter"
    INFOGRAPHIC = "infographic"


class SocialPlatform(str, PyEnum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    X = "x"
    WEBSITE = "website"


class FunnelStage(str, PyEnum):
    AWARENESS = "awareness"
    EDUCATION = "education"
    CONSIDERATION = "consideration"
    CONVERSION = "conversion"
    RETENTION = "retention"


class ContentPillar(BaseModel):
    __tablename__ = "content_pillars"

    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="pillar")
    content_ideas: Mapped[list["ContentIdea"]] = relationship(back_populates="pillar")


class Campaign(BaseModel):
    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    pillar_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content_pillars.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(50), default="active")
    start_date: Mapped[str | None] = mapped_column(String(30), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(30), nullable=True)
    budget_usd: Mapped[float | None] = mapped_column(Float, nullable=True)

    pillar: Mapped["ContentPillar | None"] = relationship(back_populates="campaigns")
    content_ideas: Mapped[list["ContentIdea"]] = relationship(back_populates="campaign")


class ContentIdea(BaseModel):
    __tablename__ = "content_ideas"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    pillar_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content_pillars.id"), nullable=True
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True
    )
    topic_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id"), nullable=True
    )
    audience: Mapped[str | None] = mapped_column(String(300), nullable=True)
    funnel_stage: Mapped[FunnelStage | None] = mapped_column(String(50), nullable=True)
    suggested_formats: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    suggested_platforms: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    priority_score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_by_agent: Mapped[bool] = mapped_column(Boolean, default=False)

    pillar: Mapped["ContentPillar | None"] = relationship(back_populates="content_ideas")
    campaign: Mapped["Campaign | None"] = relationship(back_populates="content_ideas")
    topic: Mapped["Topic | None"] = relationship(back_populates="content_ideas")  # type: ignore[name-defined]
    canonical_assets: Mapped[list["CanonicalAsset"]] = relationship(back_populates="idea")


class CanonicalAsset(BaseModel):
    """The primary content asset — all platform variants derive from this."""
    __tablename__ = "canonical_assets"

    idea_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content_ideas.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    medical_risk: Mapped[MedicalRiskLevel] = mapped_column(
        String(20), default=MedicalRiskLevel.LOW
    )
    status: Mapped[ContentStatus] = mapped_column(
        String(30), default=ContentStatus.DRAFT
    )
    brand_voice_settings: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    source_citations: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    idea: Mapped["ContentIdea | None"] = relationship(back_populates="canonical_assets")
    platform_variants: Mapped[list["PlatformVariant"]] = relationship(
        back_populates="canonical_asset"
    )
    approval_decisions: Mapped[list["ApprovalDecision"]] = relationship(
        back_populates="asset"
    )
    claim_verifications: Mapped[list["ClaimVerification"]] = relationship(
        back_populates="asset"
    )


class PlatformVariant(BaseModel):
    """Platform-specific adaptation of a canonical asset."""
    __tablename__ = "platform_variants"

    canonical_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("canonical_assets.id", ondelete="CASCADE"), nullable=False
    )
    platform: Mapped[SocialPlatform] = mapped_column(String(30), nullable=False)
    format: Mapped[ContentFormat] = mapped_column(String(50), nullable=False)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    hook: Mapped[str | None] = mapped_column(Text, nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    cta: Mapped[str | None] = mapped_column(String(300), nullable=True)
    hashtags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # platform extras
    status: Mapped[ContentStatus] = mapped_column(
        String(30), default=ContentStatus.DRAFT
    )
    language: Mapped[str] = mapped_column(String(10), default="en")

    canonical_asset: Mapped["CanonicalAsset"] = relationship(back_populates="platform_variants")
    published_posts: Mapped[list["PublishedPost"]] = relationship(
        back_populates="platform_variant"
    )


class ApprovalDecision(BaseModel):
    """Records every review decision on a canonical asset."""
    __tablename__ = "approval_decisions"

    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("canonical_assets.id", ondelete="CASCADE"), nullable=False
    )
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    review_type: Mapped[str] = mapped_column(String(50), nullable=False)  # fact_check | medical | brand
    decision: Mapped[str] = mapped_column(String(30), nullable=False)  # approved | rejected | needs_revision
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    asset_version: Mapped[int] = mapped_column(Integer, nullable=False)
    is_ai_review: Mapped[bool] = mapped_column(Boolean, default=False)

    asset: Mapped["CanonicalAsset"] = relationship(back_populates="approval_decisions")


class ClaimVerification(BaseModel):
    """Individual claim extracted and verified from a content asset."""
    __tablename__ = "claim_verifications"

    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("canonical_assets.id", ondelete="CASCADE"), nullable=False
    )
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    claim_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    verification_status: Mapped[str] = mapped_column(
        String(30), default="pending"
    )  # pending | verified | unverified | flagged
    evidence_urls: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    evidence_excerpts: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    risk_flags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    medical_risk: Mapped[str] = mapped_column(String(20), default="low")
    verified_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    asset: Mapped["CanonicalAsset"] = relationship(back_populates="claim_verifications")
