"""
Pydantic schemas for Social Account endpoints.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel


class AccountCreate(BaseModel):
    platform: str
    account_name: str
    display_name: str | None = None
    is_mock: bool = True


class AccountResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    platform: str
    account_name: str
    display_name: str | None
    profile_url: str | None
    avatar_url: str | None
    is_active: bool
    is_paused: bool
    is_mock: bool
    health_status: str
    follower_count: int | None
    subscriber_count: int | None
    created_at: datetime
