"""
Social & Publishing Models — Accounts, posts, schedules, metrics.
"""
import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.models.content import SocialPlatform


class SocialAccount(BaseModel):
    """A connected brand social media account."""
    __tablename__ = "social_accounts"

    platform: Mapped[SocialPlatform] = mapped_column(String(30), nullable=False)
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Encrypted OAuth tokens
    access_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    scopes: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False)  # emergency stop
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True)  # demo mode flag
    last_health_check: Mapped[str | None] = mapped_column(String(50), nullable=True)
    health_status: Mapped[str] = mapped_column(String(30), default="unknown")
    # Audience metadata
    follower_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subscriber_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    published_posts: Mapped[list["PublishedPost"]] = relationship(back_populates="account")
    publication_schedules: Mapped[list["PublicationSchedule"]] = relationship(
        back_populates="account"
    )


class PublicationSchedule(BaseModel):
    """A planned publication slot — not yet published."""
    __tablename__ = "publication_schedules"

    platform_variant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("platform_variants.id", ondelete="CASCADE"),
        nullable=False,
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("social_accounts.id"),
        nullable=False,
    )
    scheduled_for: Mapped[str] = mapped_column(String(50), nullable=False)  # ISO datetime
    status: Mapped[str] = mapped_column(String(30), default="pending")
    # pending | publishing | published | failed | cancelled
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    account: Mapped["SocialAccount"] = relationship(back_populates="publication_schedules")
    published_post: Mapped["PublishedPost | None"] = relationship(
        back_populates="schedule", uselist=False
    )
    publishing_attempts: Mapped[list["PublishingAttempt"]] = relationship(
        back_populates="schedule"
    )


class PublishedPost(BaseModel):
    """A confirmed published post on a social platform."""
    __tablename__ = "published_posts"

    schedule_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("publication_schedules.id"), nullable=True
    )
    platform_variant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("platform_variants.id"), nullable=False
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("social_accounts.id"), nullable=False
    )
    platform_post_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    platform_post_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    published_at: Mapped[str] = mapped_column(String(50), nullable=False)
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True)

    schedule: Mapped["PublicationSchedule | None"] = relationship(back_populates="published_post")
    platform_variant: Mapped["PlatformVariant"] = relationship(back_populates="published_posts")  # type: ignore
    account: Mapped["SocialAccount"] = relationship(back_populates="published_posts")
    metric_observations: Mapped[list["MetricObservation"]] = relationship(
        back_populates="post"
    )


class PublishingAttempt(BaseModel):
    """Records each attempt to publish — for retry and idempotency tracking."""
    __tablename__ = "publishing_attempts"

    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("publication_schedules.id"), nullable=False
    )
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)  # success | failed | timeout
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    platform_response: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON

    schedule: Mapped["PublicationSchedule"] = relationship(back_populates="publishing_attempts")


class MetricObservation(BaseModel):
    """Time-series performance metric for a published post."""
    __tablename__ = "metric_observations"

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("published_posts.id", ondelete="CASCADE"), nullable=False
    )
    observed_at: Mapped[str] = mapped_column(String(50), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # views | reach | likes | comments | shares | saves | watch_time | followers_gained
    value: Mapped[float] = mapped_column(Float, nullable=False)
    is_cumulative: Mapped[bool] = mapped_column(Boolean, default=True)
    source: Mapped[str] = mapped_column(String(50), default="api")  # api | mock | manual

    post: Mapped["PublishedPost"] = relationship(back_populates="metric_observations")


from app.models.content import PlatformVariant  # noqa: E402, F401
