"""
Publishing Service — Business logic for scheduling and publishing content.

Responsibilities (SRP):
  - Validate content is approved before scheduling
  - Check account is active and not paused
  - Prevent real publishing in demo/non-authorized modes
  - Track publishing attempts with idempotency
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import (
    NotFoundError,
    OperatingModeError,
    PublishingBlockedError,
    ValidationError,
)
from app.models.content import CanonicalAsset, ContentStatus, PlatformVariant
from app.models.social import (
    PublicationSchedule,
    PublishedPost,
    PublishingAttempt,
    SocialAccount,
)
from app.models.user import User

logger = structlog.get_logger(__name__)


class PublishingService:
    """Encapsulates all business logic for scheduling and publishing."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── Schedule ──────────────────────────────────────────────────────────
    async def schedule_variant(
        self,
        variant_id: uuid.UUID,
        account_id: uuid.UUID,
        scheduled_for: str,
        actor: User,
        idempotency_key: str | None = None,
    ) -> PublicationSchedule:
        """
        Schedule a platform variant for publishing.

        Checks:
          - Variant exists
          - Parent asset is APPROVED
          - Account is active and not paused
          - Operating mode permits scheduling
        """
        variant = await self._get_variant(variant_id)
        asset = await self._get_asset(variant.canonical_asset_id)
        account = await self._get_account(account_id)

        # Compliance checks
        if ContentStatus(asset.status) not in (ContentStatus.APPROVED, ContentStatus.SCHEDULED):
            raise ValidationError(
                f"Asset must be APPROVED before scheduling; current status: {asset.status}"
            )

        if not account.is_active:
            raise PublishingBlockedError("Social account is inactive")

        if account.is_paused:
            raise PublishingBlockedError(
                "Social account has an active emergency pause. Resume it before scheduling."
            )

        # Use provided key or generate one
        idem_key = idempotency_key or f"{variant_id}:{account_id}:{scheduled_for}"

        # Deduplicate: return existing schedule if same key
        existing_result = await self._db.execute(
            select(PublicationSchedule).where(
                PublicationSchedule.idempotency_key == idem_key
            )
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            logger.info("schedule_deduplicated", idempotency_key=idem_key)
            return existing

        schedule = PublicationSchedule(
            platform_variant_id=variant_id,
            account_id=account_id,
            scheduled_for=scheduled_for,
            idempotency_key=idem_key,
        )
        self._db.add(schedule)

        # Advance asset status to SCHEDULED
        if ContentStatus(asset.status) == ContentStatus.APPROVED:
            asset.status = ContentStatus.SCHEDULED  # type: ignore[assignment]

        logger.info(
            "content_scheduled",
            variant_id=str(variant_id),
            account_id=str(account_id),
            scheduled_for=scheduled_for,
            actor_id=str(actor.id),
        )
        return schedule

    # ── Mock Publish (demo mode) ──────────────────────────────────────────
    async def mock_publish(
        self,
        schedule_id: uuid.UUID,
        actor: User,
    ) -> PublishedPost:
        """
        Simulate publishing in demo mode — creates a mock published post.
        
        In ASSISTED or CONTROLLED mode, actual platform API calls would be
        made through platform adapters. This is intentionally mock-only.
        """
        schedule = await self._get_schedule(schedule_id)

        if schedule.status != "pending":
            raise ValidationError(
                f"Schedule is already '{schedule.status}'; only pending schedules can be published"
            )

        # Safety gate: never actually call real APIs without explicit mode
        if not settings.is_demo:
            raise OperatingModeError(
                "real_publish",
                settings.OPERATING_MODE,
            )

        account = await self._get_account(schedule.account_id)
        if account.is_paused:
            raise PublishingBlockedError("Account is paused — emergency stop is active")

        # Record attempt
        attempt = PublishingAttempt(
            schedule_id=schedule_id,
            attempt_number=1,
            status="success",
            platform_response='{"mock": true}',
        )
        self._db.add(attempt)

        # Create mock published post
        published_at = datetime.now(timezone.utc).isoformat()
        post = PublishedPost(
            schedule_id=schedule_id,
            platform_variant_id=schedule.platform_variant_id,
            account_id=schedule.account_id,
            platform_post_id=f"mock_{uuid.uuid4().hex[:8]}",
            platform_post_url="https://demo.metago.in/mock-post",
            published_at=published_at,
            is_mock=True,
        )
        self._db.add(post)

        schedule.status = "published"

        logger.info(
            "mock_publish_success",
            schedule_id=str(schedule_id),
            actor_id=str(actor.id),
        )
        return post

    # ── Private helpers ────────────────────────────────────────────────────
    async def _get_variant(self, variant_id: uuid.UUID) -> PlatformVariant:
        result = await self._db.execute(
            select(PlatformVariant).where(PlatformVariant.id == variant_id)
        )
        variant = result.scalar_one_or_none()
        if not variant:
            raise NotFoundError("PlatformVariant", str(variant_id))
        return variant

    async def _get_asset(self, asset_id: uuid.UUID) -> CanonicalAsset:
        result = await self._db.execute(
            select(CanonicalAsset).where(CanonicalAsset.id == asset_id)
        )
        asset = result.scalar_one_or_none()
        if not asset:
            raise NotFoundError("Asset", str(asset_id))
        return asset

    async def _get_account(self, account_id: uuid.UUID) -> SocialAccount:
        result = await self._db.execute(
            select(SocialAccount).where(SocialAccount.id == account_id)
        )
        account = result.scalar_one_or_none()
        if not account:
            raise NotFoundError("SocialAccount", str(account_id))
        return account

    async def _get_schedule(self, schedule_id: uuid.UUID) -> PublicationSchedule:
        result = await self._db.execute(
            select(PublicationSchedule).where(PublicationSchedule.id == schedule_id)
        )
        schedule = result.scalar_one_or_none()
        if not schedule:
            raise NotFoundError("PublicationSchedule", str(schedule_id))
        return schedule
