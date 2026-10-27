"""
Analytics API — Metrics overview and per-post performance.
"""
import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.content import CanonicalAsset, ContentStatus
from app.models.social import MetricObservation, PublishedPost, SocialAccount

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def overview(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """Dashboard overview metrics."""
    total_assets = await db.scalar(select(func.count(CanonicalAsset.id)))
    published_assets = await db.scalar(
        select(func.count(CanonicalAsset.id)).where(
            CanonicalAsset.status == ContentStatus.PUBLISHED
        )
    )
    pending_review = await db.scalar(
        select(func.count(CanonicalAsset.id)).where(
            CanonicalAsset.status.in_(
                [ContentStatus.FACT_CHECK, ContentStatus.MEDICAL_REVIEW, ContentStatus.BRAND_REVIEW]
            )
        )
    )
    total_posts = await db.scalar(select(func.count(PublishedPost.id)))
    connected_accounts = await db.scalar(
        select(func.count(SocialAccount.id)).where(SocialAccount.is_active == True)  # noqa: E712
    )

    return {
        "total_assets": total_assets or 0,
        "published_assets": published_assets or 0,
        "pending_review": pending_review or 0,
        "total_posts": total_posts or 0,
        "connected_accounts": connected_accounts or 0,
    }


@router.get("/posts/{post_id}/metrics")
async def post_metrics(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """Return metric time-series for a published post."""
    result = await db.execute(
        select(MetricObservation)
        .where(MetricObservation.post_id == post_id)
        .order_by(MetricObservation.observed_at)
    )
    obs = result.scalars().all()
    return {
        "post_id": post_id,
        "observations": [
            {
                "metric_name": o.metric_name,
                "value": o.value,
                "observed_at": o.observed_at,
                "source": o.source,
            }
            for o in obs
        ],
    }
