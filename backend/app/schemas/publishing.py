"""
Pydantic schemas for Publishing endpoints.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel


class ScheduleCreate(BaseModel):
    """Request body to schedule a platform variant."""
    variant_id: uuid.UUID
    account_id: uuid.UUID
    scheduled_for: str  # ISO datetime string
    idempotency_key: str | None = None


class ScheduleResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    platform_variant_id: uuid.UUID
    account_id: uuid.UUID
    scheduled_for: str
    status: str
    idempotency_key: str
    notes: str | None
    created_at: datetime


class PublishedPostResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    schedule_id: uuid.UUID | None
    platform_variant_id: uuid.UUID
    account_id: uuid.UUID
    platform_post_id: str | None
    platform_post_url: str | None
    published_at: str
    is_mock: bool
    created_at: datetime
