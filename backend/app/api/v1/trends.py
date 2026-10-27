"""
Trends API — Topics, observations, research sources.
"""
import uuid
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.trend import ResearchSource, Topic, TrendObservation
from app.schemas.trends import (
    SourceResponse,
    TopicCreate,
    TopicResponse,
    ObservationCreate,
    ObservationResponse,
)

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("/topics", response_model=list[TopicResponse])
async def list_topics(
    is_trending: bool | None = Query(None),
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(Topic).order_by(Topic.final_score.desc())
    if is_trending is not None:
        q = q.where(Topic.is_trending == is_trending)
    if category:
        q = q.where(Topic.category == category)
    result = await db.execute(q.limit(100))
    return [TopicResponse.model_validate(t) for t in result.scalars().all()]


@router.post("/topics", response_model=TopicResponse, status_code=201)
async def create_topic(
    body: TopicCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    from python_slugify import slugify
    topic = Topic(
        title=body.title,
        slug=slugify(body.title),
        category=body.category,
        is_evergreen=body.is_evergreen,
        medical_risk=body.medical_risk,
        related_terms=body.related_terms,
        audience_relevance=body.audience_relevance,
    )
    db.add(topic)
    await db.flush()
    await db.refresh(topic)
    return TopicResponse.model_validate(topic)


@router.get("/topics/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    result = await db.execute(select(Topic).where(Topic.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise NotFoundError("Topic", str(topic_id))
    return TopicResponse.model_validate(topic)


@router.post("/topics/{topic_id}/observations", response_model=ObservationResponse, status_code=201)
async def add_observation(
    topic_id: uuid.UUID,
    body: ObservationCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    obs = TrendObservation(
        topic_id=topic_id,
        source=body.source,
        source_url=body.source_url,
        raw_value=body.raw_value,
        metric_name=body.metric_name,
        growth_rate=body.growth_rate,
        geographic_focus=body.geographic_focus or "IN",
        observed_at=datetime.now(timezone.utc).isoformat(),
        raw_data=body.raw_data,
    )
    db.add(obs)
    await db.flush()
    await db.refresh(obs)
    return ObservationResponse.model_validate(obs)


@router.get("/sources", response_model=list[SourceResponse])
async def list_sources(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    result = await db.execute(
        select(ResearchSource)
        .where(ResearchSource.is_stale == False)  # noqa: E712
        .order_by(ResearchSource.reliability_score.desc())
        .limit(50)
    )
    return [SourceResponse.model_validate(s) for s in result.scalars().all()]
