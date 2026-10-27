"""
Models __init__ — register all models so Alembic can discover them.
"""
from app.db.base import Base  # noqa: F401
from app.models.user import User, RefreshToken, AuditEvent  # noqa: F401
from app.models.content import (  # noqa: F401
    ContentPillar,
    Campaign,
    ContentIdea,
    CanonicalAsset,
    PlatformVariant,
    ApprovalDecision,
    ClaimVerification,
)
from app.models.trend import Topic, TrendObservation, ResearchSource  # noqa: F401
from app.models.social import (  # noqa: F401
    SocialAccount,
    PublicationSchedule,
    PublishedPost,
    PublishingAttempt,
    MetricObservation,
)

__all__ = [
    "Base",
    "User", "RefreshToken", "AuditEvent",
    "ContentPillar", "Campaign", "ContentIdea",
    "CanonicalAsset", "PlatformVariant",
    "ApprovalDecision", "ClaimVerification",
    "Topic", "TrendObservation", "ResearchSource",
    "SocialAccount", "PublicationSchedule",
    "PublishedPost", "PublishingAttempt", "MetricObservation",
]
