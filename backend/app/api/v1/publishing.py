"""
Publishing API — Schedule and publish platform variants.

Routes delegate to PublishingService for all compliance and business logic.
"""
import uuid

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_user, require_content_manager
from app.db.session import get_db
from app.models.social import PublicationSchedule, PublishedPost
from app.models.user import User
from app.schemas.publishing import PublishedPostResponse, ScheduleCreate, ScheduleResponse
from app.services.publishing import PublishingService

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/publishing", tags=["publishing"])


# ── Dependency: PublishingService ─────────────────────────────────────────
def get_publishing_service(db: AsyncSession = Depends(get_db)) -> PublishingService:
    return PublishingService(db)


# ── Schedules ────────────────────────────────────────────────────────────
@router.get("/schedules", response_model=list[ScheduleResponse])
async def list_schedules(
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List publication schedules, optionally filtered by status."""
    q = select(PublicationSchedule).order_by(PublicationSchedule.scheduled_for)
    if status:
        q = q.where(PublicationSchedule.status == status)
    result = await db.execute(q.limit(100))
    return [ScheduleResponse.model_validate(s) for s in result.scalars().all()]


@router.post("/schedules", response_model=ScheduleResponse, status_code=201)
async def create_schedule(
    body: ScheduleCreate,
    service: PublishingService = Depends(get_publishing_service),
    user: User = Depends(require_content_manager()),
):
    """
    Schedule a platform variant for publishing on a social account.

    Enforces:
    - Parent asset must be APPROVED
    - Account must be active and not paused
    - Idempotency: duplicate requests return the existing schedule
    """
    schedule = await service.schedule_variant(
        variant_id=body.variant_id,
        account_id=body.account_id,
        scheduled_for=body.scheduled_for,
        actor=user,
        idempotency_key=body.idempotency_key,
    )
    await service._db.flush()
    await service._db.refresh(schedule)
    return ScheduleResponse.model_validate(schedule)


# ── Mock Publish ──────────────────────────────────────────────────────────
@router.post(
    "/schedules/{schedule_id}/publish",
    response_model=PublishedPostResponse,
    status_code=201,
)
async def mock_publish(
    schedule_id: uuid.UUID,
    service: PublishingService = Depends(get_publishing_service),
    user: User = Depends(require_content_manager()),
):
    """
    Execute a mock publish for a scheduled item (DEMO mode only).

    In ASSISTED/CONTROLLED modes, this endpoint will call real platform adapters.
    Currently only DEMO (mock) publishing is supported.
    """
    post = await service.mock_publish(schedule_id=schedule_id, actor=user)
    await service._db.flush()
    await service._db.refresh(post)
    return PublishedPostResponse.model_validate(post)


# ── Published Posts ───────────────────────────────────────────────────────
@router.get("/posts", response_model=list[PublishedPostResponse])
async def list_published_posts(
    account_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List published posts, optionally filtered by account."""
    q = select(PublishedPost).order_by(PublishedPost.published_at.desc())
    if account_id:
        q = q.where(PublishedPost.account_id == account_id)
    result = await db.execute(q.limit(100))
    return [PublishedPostResponse.model_validate(p) for p in result.scalars().all()]
