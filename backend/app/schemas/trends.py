"""
Pydantic schemas for Trends endpoints.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel


class TopicCreate(BaseModel):
    title: str
    category: str | None = None
    is_evergreen: bool = False
    medical_risk: str = "low"
    related_terms: str | None = None
    audience_relevance: float = 0.5


class TopicResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    title: str
    slug: str
    category: str | None
    is_evergreen: bool
    is_trending: bool
    medical_risk: str
    content_saturation: float
    audience_relevance: float
    final_score: float
    created_at: datetime


class ObservationCreate(BaseModel):
    source: str
    source_url: str | None = None
    raw_value: float | None = None
    metric_name: str | None = None
    growth_rate: float | None = None
    geographic_focus: str | None = "IN"
    raw_data: str | None = None


class ObservationResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    topic_id: uuid.UUID
    source: str
    source_url: str | None
    raw_value: float | None
    metric_name: str | None
    growth_rate: float | None
    geographic_focus: str | None
    observed_at: str
    created_at: datetime


class SourceResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    url: str
    title: str | None
    source_type: str
    domain: str | None
    publication_date: str | None
    retrieved_at: str
    reliability_score: float
    is_stale: bool
