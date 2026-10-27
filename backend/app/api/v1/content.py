"""
Content API — CRUD for pillars, campaigns, ideas, assets, variants, and approval workflow.
Routes delegate business logic to ContentService (DIP / SRP).
"""
import uuid

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_user, require_content_manager
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.content import (
    CanonicalAsset,
    ClaimVerification,
    ContentIdea,
    ContentPillar,
    ContentStatus,
    PlatformVariant,
)
from app.models.user import User
from app.schemas.content import (
    ApprovalRequest,
    ApprovalResponse,
    AssetCreate,
    AssetResponse,
    ClaimResponse,
    IdeaCreate,
    IdeaResponse,
    PillarCreate,
    PillarResponse,
    StatusTransitionRequest,
    VariantCreate,
    VariantResponse,
)
from app.services.content import ContentService

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/content", tags=["content"])


# ── Dependency: ContentService ────────────────────────────────────────────
def get_content_service(db: AsyncSession = Depends(get_db)) -> ContentService:
    """Provide a ContentService bound to the current request's DB session."""
    return ContentService(db)


# ── Content Pillars ──────────────────────────────────────────────────────
@router.get("/pillars", response_model=list[PillarResponse])
async def list_pillars(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ContentPillar)
        .where(ContentPillar.is_active == True)  # noqa: E712
        .order_by(ContentPillar.sort_order)
    )
    return [PillarResponse.model_validate(p) for p in result.scalars().all()]


@router.post("/pillars", response_model=PillarResponse, status_code=201)
async def create_pillar(
    body: PillarCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_content_manager()),
):
    from python_slugify import slugify

    pillar = ContentPillar(
        name=body.name,
        slug=slugify(body.name),
        description=body.description,
    )
    db.add(pillar)
    await db.flush()
    await db.refresh(pillar)
    return PillarResponse.model_validate(pillar)


# ── Content Ideas ────────────────────────────────────────────────────────
@router.get("/ideas", response_model=list[IdeaResponse])
async def list_ideas(
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = select(ContentIdea)
    if status:
        q = q.where(ContentIdea.status == status)
    result = await db.execute(q.order_by(ContentIdea.priority_score.desc()))
    return [IdeaResponse.model_validate(i) for i in result.scalars().all()]


@router.post("/ideas", response_model=IdeaResponse, status_code=201)
async def create_idea(
    body: IdeaCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_content_manager()),
):
    idea = ContentIdea(**body.model_dump())
    db.add(idea)
    await db.flush()
    await db.refresh(idea)
    logger.info("idea_created", idea_id=str(idea.id), user_id=str(user.id))
    return IdeaResponse.model_validate(idea)


# ── Canonical Assets ─────────────────────────────────────────────────────
@router.get("/assets", response_model=list[AssetResponse])
async def list_assets(
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = select(CanonicalAsset)
    if status:
        q = q.where(CanonicalAsset.status == status)
    result = await db.execute(q.order_by(CanonicalAsset.created_at.desc()))
    return [AssetResponse.model_validate(a) for a in result.scalars().all()]


@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: uuid.UUID,
    service: ContentService = Depends(get_content_service),
    _: User = Depends(get_current_user),
):
    asset = await service.get_asset(asset_id)
    return AssetResponse.model_validate(asset)


@router.post("/assets", response_model=AssetResponse, status_code=201)
async def create_asset(
    body: AssetCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_content_manager()),
):
    asset = CanonicalAsset(**body.model_dump(), created_by_id=user.id)
    db.add(asset)
    await db.flush()
    await db.refresh(asset)
    logger.info("asset_created", asset_id=str(asset.id))
    return AssetResponse.model_validate(asset)


# ── Status Transition ─────────────────────────────────────────────────────
@router.patch("/assets/{asset_id}/status", response_model=AssetResponse)
async def transition_asset_status(
    asset_id: uuid.UUID,
    body: StatusTransitionRequest,
    service: ContentService = Depends(get_content_service),
    user: User = Depends(require_content_manager()),
):
    """
    Transition a content asset to a new lifecycle status.
    
    Enforces the content state machine and medical compliance gate.
    HIGH/CRITICAL risk assets cannot be APPROVED without a human medical review.
    """
    asset = await service.transition_status(
        asset_id=asset_id,
        target_status=ContentStatus(body.status),
        actor=user,
        comment=body.comment,
    )
    return AssetResponse.model_validate(asset)


# ── Approval Decisions ────────────────────────────────────────────────────
@router.post("/assets/{asset_id}/approvals", response_model=ApprovalResponse, status_code=201)
async def record_approval(
    asset_id: uuid.UUID,
    body: ApprovalRequest,
    service: ContentService = Depends(get_content_service),
    user: User = Depends(get_current_user),
):
    """
    Record a review decision (fact_check | medical | brand).
    
    Only MEDICAL_REVIEWER or SUPER_ADMIN roles can record medical decisions.
    Approvals auto-advance the asset status through the pipeline.
    """
    approval = await service.record_approval(
        asset_id=asset_id,
        review_type=body.review_type,
        decision=body.decision,
        reviewer=user,
        comments=body.comments,
    )
    await service._db.flush()
    await service._db.refresh(approval)
    return ApprovalResponse.model_validate(approval)


# ── Claims ────────────────────────────────────────────────────────────────
@router.get("/assets/{asset_id}/claims", response_model=list[ClaimResponse])
async def list_claims(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ClaimVerification).where(ClaimVerification.asset_id == asset_id)
    )
    return [ClaimResponse.model_validate(c) for c in result.scalars().all()]


# ── Platform Variants ────────────────────────────────────────────────────
@router.get("/assets/{asset_id}/variants", response_model=list[VariantResponse])
async def list_variants(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PlatformVariant).where(PlatformVariant.canonical_asset_id == asset_id)
    )
    return [VariantResponse.model_validate(v) for v in result.scalars().all()]


@router.post("/assets/{asset_id}/variants", response_model=VariantResponse, status_code=201)
async def create_variant(
    asset_id: uuid.UUID,
    body: VariantCreate,
    service: ContentService = Depends(get_content_service),
    _: User = Depends(require_content_manager()),
):
    # Verify asset exists via service
    await service.get_asset(asset_id)

    variant = PlatformVariant(**body.model_dump(), canonical_asset_id=asset_id)
    service._db.add(variant)
    await service._db.flush()
    await service._db.refresh(variant)
    return VariantResponse.model_validate(variant)
