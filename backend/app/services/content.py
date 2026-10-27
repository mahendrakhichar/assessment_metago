"""
Content Service — Business logic for canonical assets and approval workflow.

Responsibilities (SRP):
  - Asset status state machine enforcement
  - Approval decision recording and status transitions
  - Medical gate enforcement
  - Claim verification management

All DB operations go through an injected AsyncSession (DIP).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    MedicalReviewRequiredError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.models.content import (
    ApprovalDecision,
    CanonicalAsset,
    ClaimVerification,
    ContentIdea,
    ContentStatus,
    MedicalRiskLevel,
)
from app.models.user import User, UserRole

logger = structlog.get_logger(__name__)

# ── Allowed status transitions (state machine) ─────────────────────────────
_ALLOWED_TRANSITIONS: dict[ContentStatus, set[ContentStatus]] = {
    ContentStatus.DRAFT: {ContentStatus.FACT_CHECK, ContentStatus.ARCHIVED},
    ContentStatus.FACT_CHECK: {
        ContentStatus.MEDICAL_REVIEW,
        ContentStatus.BRAND_REVIEW,
        ContentStatus.REVISION_REQUESTED,
        ContentStatus.BLOCKED,
    },
    ContentStatus.MEDICAL_REVIEW: {
        ContentStatus.BRAND_REVIEW,
        ContentStatus.REVISION_REQUESTED,
        ContentStatus.BLOCKED,
    },
    ContentStatus.BRAND_REVIEW: {
        ContentStatus.APPROVED,
        ContentStatus.REVISION_REQUESTED,
        ContentStatus.BLOCKED,
    },
    ContentStatus.REVISION_REQUESTED: {ContentStatus.DRAFT, ContentStatus.FACT_CHECK},
    ContentStatus.APPROVED: {ContentStatus.SCHEDULED, ContentStatus.DRAFT},
    ContentStatus.SCHEDULED: {ContentStatus.PUBLISHED, ContentStatus.APPROVED},
    ContentStatus.PUBLISHED: set(),  # terminal — no outgoing transitions
    ContentStatus.BLOCKED: {ContentStatus.DRAFT},  # can be unblocked back to draft
    ContentStatus.ARCHIVED: set(),  # terminal
}


class ContentService:
    """Encapsulates all business logic for content asset lifecycle."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── Retrieval ──────────────────────────────────────────────────────────
    async def get_asset(self, asset_id: uuid.UUID) -> CanonicalAsset:
        result = await self._db.execute(
            select(CanonicalAsset).where(CanonicalAsset.id == asset_id)
        )
        asset = result.scalar_one_or_none()
        if not asset:
            raise NotFoundError("Asset", str(asset_id))
        return asset

    async def get_idea(self, idea_id: uuid.UUID) -> ContentIdea:
        result = await self._db.execute(
            select(ContentIdea).where(ContentIdea.id == idea_id)
        )
        idea = result.scalar_one_or_none()
        if not idea:
            raise NotFoundError("ContentIdea", str(idea_id))
        return idea

    # ── Status transitions ─────────────────────────────────────────────────
    async def transition_status(
        self,
        asset_id: uuid.UUID,
        target_status: ContentStatus,
        actor: User,
        comment: str | None = None,
    ) -> CanonicalAsset:
        """
        Apply a status transition with all compliance checks.

        Enforces:
          - Valid state machine transition
          - Medical gate: HIGH/CRITICAL risk content cannot skip medical_review
          - Role-based permission on the transition
        """
        asset = await self.get_asset(asset_id)

        current = ContentStatus(asset.status)
        if target_status not in _ALLOWED_TRANSITIONS.get(current, set()):
            raise ValidationError(
                f"Cannot transition from '{current}' to '{target_status}'"
            )

        # Medical gate: HIGH/CRITICAL cannot be approved without medical review
        if target_status == ContentStatus.APPROVED:
            await self._assert_medical_gate(asset, actor)

        # Role check for specific transitions
        self._assert_transition_permission(target_status, actor)

        asset.status = target_status  # type: ignore[assignment]
        asset.updated_at = datetime.now(timezone.utc)  # type: ignore[assignment]

        logger.info(
            "content_status_transition",
            asset_id=str(asset_id),
            from_status=current,
            to_status=target_status,
            actor_id=str(actor.id),
        )
        return asset

    # ── Approval decisions ─────────────────────────────────────────────────
    async def record_approval(
        self,
        asset_id: uuid.UUID,
        review_type: str,
        decision: str,
        reviewer: User,
        comments: str | None = None,
        is_ai_review: bool = False,
    ) -> ApprovalDecision:
        """
        Record an approval decision and advance the asset status accordingly.

        review_type: 'fact_check' | 'medical' | 'brand'
        decision:    'approved' | 'rejected' | 'needs_revision'
        """
        asset = await self.get_asset(asset_id)

        # Only medical reviewers or admins can record medical reviews
        if review_type == "medical" and not reviewer.can_approve_medical():
            raise PermissionDeniedError(
                "Only MEDICAL_REVIEWER or SUPER_ADMIN roles can record medical decisions"
            )

        approval = ApprovalDecision(
            asset_id=asset_id,
            reviewer_id=reviewer.id,
            review_type=review_type,
            decision=decision,
            comments=comments,
            asset_version=asset.version,
            is_ai_review=is_ai_review,
        )
        self._db.add(approval)

        # Auto-advance status on approval
        if decision == "approved":
            target = self._next_status_for_review(review_type, ContentStatus(asset.status))
            if target:
                asset.status = target  # type: ignore[assignment]
                asset.updated_at = datetime.now(timezone.utc)  # type: ignore[assignment]
        elif decision in ("rejected", "needs_revision"):
            asset.status = ContentStatus.REVISION_REQUESTED  # type: ignore[assignment]
            asset.updated_at = datetime.now(timezone.utc)  # type: ignore[assignment]

        logger.info(
            "approval_recorded",
            asset_id=str(asset_id),
            review_type=review_type,
            decision=decision,
            reviewer_id=str(reviewer.id),
        )
        return approval

    # ── Claim verifications ────────────────────────────────────────────────
    async def add_claim(
        self,
        asset_id: uuid.UUID,
        claim_text: str,
        claim_category: str | None = None,
        medical_risk: str = "low",
    ) -> ClaimVerification:
        """Add a claim extracted from an asset for verification."""
        await self.get_asset(asset_id)  # verify exists
        claim = ClaimVerification(
            asset_id=asset_id,
            claim_text=claim_text,
            claim_category=claim_category,
            medical_risk=medical_risk,
        )
        self._db.add(claim)
        return claim

    async def verify_claim(
        self,
        claim_id: uuid.UUID,
        status: str,
        reviewer: User,
        evidence_urls: str | None = None,
        risk_flags: str | None = None,
    ) -> ClaimVerification:
        """Mark a claim as verified/unverified/flagged."""
        result = await self._db.execute(
            select(ClaimVerification).where(ClaimVerification.id == claim_id)
        )
        claim = result.scalar_one_or_none()
        if not claim:
            raise NotFoundError("ClaimVerification", str(claim_id))

        claim.verification_status = status
        claim.verified_by_id = reviewer.id  # type: ignore[assignment]
        if evidence_urls:
            claim.evidence_urls = evidence_urls
        if risk_flags:
            claim.risk_flags = risk_flags

        return claim

    # ── Private helpers ────────────────────────────────────────────────────
    async def _assert_medical_gate(
        self, asset: CanonicalAsset, actor: User
    ) -> None:
        """HIGH/CRITICAL risk content must have an approved medical review."""
        risk = MedicalRiskLevel(asset.medical_risk)
        if risk not in (MedicalRiskLevel.HIGH, MedicalRiskLevel.CRITICAL):
            return  # Low/medium: no gate

        # Check if a human (non-AI) medical approval exists for this asset version
        result = await self._db.execute(
            select(ApprovalDecision).where(
                ApprovalDecision.asset_id == asset.id,
                ApprovalDecision.review_type == "medical",
                ApprovalDecision.decision == "approved",
                ApprovalDecision.is_ai_review == False,  # noqa: E712
                ApprovalDecision.asset_version == asset.version,
            )
        )
        human_approval = result.scalar_one_or_none()
        if not human_approval:
            raise MedicalReviewRequiredError()

    @staticmethod
    def _assert_transition_permission(
        target: ContentStatus, actor: User
    ) -> None:
        """Enforce role requirements for specific transitions."""
        if target == ContentStatus.APPROVED and not actor.can_manage_content():
            raise PermissionDeniedError("Only Content Managers or above can approve content")
        if target == ContentStatus.PUBLISHED and not actor.can_manage_content():
            raise PermissionDeniedError("Only Content Managers or above can publish content")

    @staticmethod
    def _next_status_for_review(
        review_type: str, current: ContentStatus
    ) -> ContentStatus | None:
        """Map review completion to the next pipeline status."""
        mapping: dict[str, ContentStatus] = {
            "fact_check": ContentStatus.MEDICAL_REVIEW,
            "medical": ContentStatus.BRAND_REVIEW,
            "brand": ContentStatus.APPROVED,
        }
        return mapping.get(review_type)
