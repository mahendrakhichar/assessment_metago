"""
Unit tests for ContentService — state machine, medical gate, approval workflow.

Uses an in-memory SQLite database (aiosqlite) for isolation.
"""
import asyncio
import uuid
import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models import *  # noqa: F401, F403 — registers all models for table creation
from app.models.content import CanonicalAsset, ContentStatus, MedicalRiskLevel, ApprovalDecision
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.core.exceptions import (
    MedicalReviewRequiredError,
    ValidationError,
    PermissionDeniedError,
)
from app.services.content import ContentService

# ── Test DB setup ──────────────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a fresh in-memory DB for each test."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# ── Fixtures ───────────────────────────────────────────────────────────────
def make_user(role: UserRole = UserRole.CONTENT_MANAGER) -> User:
    return User(
        id=uuid.uuid4(),
        email=f"user_{uuid.uuid4().hex[:6]}@test.com",
        full_name="Test User",
        hashed_password=hash_password("testpass"),
        role=role,
        is_active=True,
        is_verified=True,
    )


def make_asset(
    status: ContentStatus = ContentStatus.DRAFT,
    medical_risk: MedicalRiskLevel = MedicalRiskLevel.LOW,
) -> CanonicalAsset:
    return CanonicalAsset(
        id=uuid.uuid4(),
        title="Test Content Asset",
        body="Test body content",
        summary="Test summary",
        status=status,
        medical_risk=medical_risk,
        version=1,
    )


# ── ContentService tests ───────────────────────────────────────────────────
class TestContentServiceStateMachine:
    """Tests for valid and invalid status transitions."""

    @pytest.mark.asyncio
    async def test_valid_transition_draft_to_fact_check(self, db_session):
        user = make_user()
        asset = make_asset()
        db_session.add(user)
        db_session.add(asset)
        await db_session.flush()

        service = ContentService(db_session)
        result = await service.transition_status(
            asset_id=asset.id,
            target_status=ContentStatus.FACT_CHECK,
            actor=user,
        )
        assert result.status == ContentStatus.FACT_CHECK

    @pytest.mark.asyncio
    async def test_invalid_transition_draft_to_approved_raises(self, db_session):
        user = make_user(UserRole.SUPER_ADMIN)
        asset = make_asset(ContentStatus.DRAFT)
        db_session.add(user)
        db_session.add(asset)
        await db_session.flush()

        service = ContentService(db_session)
        with pytest.raises(ValidationError, match="Cannot transition"):
            await service.transition_status(
                asset_id=asset.id,
                target_status=ContentStatus.APPROVED,
                actor=user,
            )

    @pytest.mark.asyncio
    async def test_published_is_terminal_no_outgoing(self, db_session):
        user = make_user(UserRole.SUPER_ADMIN)
        asset = make_asset(ContentStatus.PUBLISHED)
        db_session.add(user)
        db_session.add(asset)
        await db_session.flush()

        service = ContentService(db_session)
        with pytest.raises(ValidationError):
            await service.transition_status(
                asset_id=asset.id,
                target_status=ContentStatus.DRAFT,
                actor=user,
            )

    @pytest.mark.asyncio
    async def test_not_found_raises(self, db_session):
        user = make_user()
        db_session.add(user)
        await db_session.flush()

        from app.core.exceptions import NotFoundError
        service = ContentService(db_session)
        with pytest.raises(NotFoundError):
            await service.transition_status(
                asset_id=uuid.uuid4(),
                target_status=ContentStatus.FACT_CHECK,
                actor=user,
            )


class TestMedicalGate:
    """Tests for the HIGH/CRITICAL medical review gate."""

    @pytest.mark.asyncio
    async def test_low_risk_can_be_approved_without_medical_review(self, db_session):
        admin = make_user(UserRole.SUPER_ADMIN)
        asset = make_asset(ContentStatus.BRAND_REVIEW, MedicalRiskLevel.LOW)
        db_session.add(admin)
        db_session.add(asset)
        await db_session.flush()

        service = ContentService(db_session)
        result = await service.transition_status(
            asset_id=asset.id,
            target_status=ContentStatus.APPROVED,
            actor=admin,
        )
        assert result.status == ContentStatus.APPROVED

    @pytest.mark.asyncio
    async def test_high_risk_blocked_without_medical_review(self, db_session):
        admin = make_user(UserRole.SUPER_ADMIN)
        asset = make_asset(ContentStatus.BRAND_REVIEW, MedicalRiskLevel.HIGH)
        db_session.add(admin)
        db_session.add(asset)
        await db_session.flush()

        service = ContentService(db_session)
        with pytest.raises(MedicalReviewRequiredError):
            await service.transition_status(
                asset_id=asset.id,
                target_status=ContentStatus.APPROVED,
                actor=admin,
            )

    @pytest.mark.asyncio
    async def test_high_risk_allowed_after_human_medical_review(self, db_session):
        admin = make_user(UserRole.SUPER_ADMIN)
        asset = make_asset(ContentStatus.BRAND_REVIEW, MedicalRiskLevel.HIGH)
        medical_reviewer = make_user(UserRole.MEDICAL_REVIEWER)
        db_session.add(admin)
        db_session.add(asset)
        db_session.add(medical_reviewer)

        # Record a human medical approval
        approval = ApprovalDecision(
            asset_id=asset.id,
            reviewer_id=medical_reviewer.id,
            review_type="medical",
            decision="approved",
            asset_version=1,
            is_ai_review=False,
        )
        db_session.add(approval)
        await db_session.flush()

        service = ContentService(db_session)
        result = await service.transition_status(
            asset_id=asset.id,
            target_status=ContentStatus.APPROVED,
            actor=admin,
        )
        assert result.status == ContentStatus.APPROVED

    @pytest.mark.asyncio
    async def test_ai_review_does_not_satisfy_medical_gate(self, db_session):
        """An AI medical approval does NOT satisfy the medical gate."""
        admin = make_user(UserRole.SUPER_ADMIN)
        asset = make_asset(ContentStatus.BRAND_REVIEW, MedicalRiskLevel.HIGH)
        db_session.add(admin)
        db_session.add(asset)

        # AI review — should NOT unblock the gate
        ai_approval = ApprovalDecision(
            asset_id=asset.id,
            reviewer_id=None,
            review_type="medical",
            decision="approved",
            asset_version=1,
            is_ai_review=True,  # <-- AI review
        )
        db_session.add(ai_approval)
        await db_session.flush()

        service = ContentService(db_session)
        with pytest.raises(MedicalReviewRequiredError):
            await service.transition_status(
                asset_id=asset.id,
                target_status=ContentStatus.APPROVED,
                actor=admin,
            )


class TestApprovalWorkflow:
    """Tests for recording approval decisions."""

    @pytest.mark.asyncio
    async def test_brand_approval_advances_to_approved(self, db_session):
        manager = make_user(UserRole.CONTENT_MANAGER)
        asset = make_asset(ContentStatus.BRAND_REVIEW, MedicalRiskLevel.LOW)
        db_session.add(manager)
        db_session.add(asset)
        await db_session.flush()

        service = ContentService(db_session)
        approval = await service.record_approval(
            asset_id=asset.id,
            review_type="brand",
            decision="approved",
            reviewer=manager,
        )
        assert approval.decision == "approved"
        assert asset.status == ContentStatus.APPROVED

    @pytest.mark.asyncio
    async def test_rejection_moves_to_revision_requested(self, db_session):
        manager = make_user(UserRole.CONTENT_MANAGER)
        asset = make_asset(ContentStatus.BRAND_REVIEW)
        db_session.add(manager)
        db_session.add(asset)
        await db_session.flush()

        service = ContentService(db_session)
        await service.record_approval(
            asset_id=asset.id,
            review_type="brand",
            decision="rejected",
            reviewer=manager,
            comments="Needs stronger CTA",
        )
        assert asset.status == ContentStatus.REVISION_REQUESTED

    @pytest.mark.asyncio
    async def test_viewer_cannot_record_medical_review(self, db_session):
        viewer = make_user(UserRole.VIEWER)
        asset = make_asset(ContentStatus.MEDICAL_REVIEW)
        db_session.add(viewer)
        db_session.add(asset)
        await db_session.flush()

        service = ContentService(db_session)
        with pytest.raises(PermissionDeniedError):
            await service.record_approval(
                asset_id=asset.id,
                review_type="medical",
                decision="approved",
                reviewer=viewer,
            )

    @pytest.mark.asyncio
    async def test_medical_reviewer_can_record_medical_review(self, db_session):
        reviewer = make_user(UserRole.MEDICAL_REVIEWER)
        asset = make_asset(ContentStatus.MEDICAL_REVIEW)
        db_session.add(reviewer)
        db_session.add(asset)
        await db_session.flush()

        service = ContentService(db_session)
        approval = await service.record_approval(
            asset_id=asset.id,
            review_type="medical",
            decision="approved",
            reviewer=reviewer,
        )
        assert approval.review_type == "medical"
        assert approval.decision == "approved"
