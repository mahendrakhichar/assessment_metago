"""
Trend Models — Trend observations, topics, research sources.
"""
import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class Topic(BaseModel):
    """Normalized, deduplicated topic entity."""
    __tablename__ = "topics"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(500), nullable=False, unique=True, index=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)  # glp1 | obesity | nutrition...
    is_evergreen: Mapped[bool] = mapped_column(Boolean, default=False)
    is_trending: Mapped[bool] = mapped_column(Boolean, default=False)
    medical_risk: Mapped[str] = mapped_column(String(20), default="low")
    related_terms: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    competitor_coverage: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    content_saturation: Mapped[float] = mapped_column(Float, default=0.0)  # 0-1
    audience_relevance: Mapped[float] = mapped_column(Float, default=0.0)  # 0-1
    final_score: Mapped[float] = mapped_column(Float, default=0.0)
    last_scored_at: Mapped[str | None] = mapped_column(String(50), nullable=True)

    observations: Mapped[list["TrendObservation"]] = relationship(back_populates="topic")
    content_ideas: Mapped[list["ContentIdea"]] = relationship(back_populates="topic")  # type: ignore


class TrendObservation(BaseModel):
    """A single observed data point for a topic from a specific source."""
    __tablename__ = "trend_observations"

    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)  # google_trends | youtube | rss...
    source_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    raw_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    metric_name: Mapped[str | None] = mapped_column(String(100), nullable=True)  # search_volume | views...
    growth_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    geographic_focus: Mapped[str | None] = mapped_column(String(100), nullable=True)
    observed_at: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON for source-specific data

    topic: Mapped["Topic"] = relationship(back_populates="observations")


class ResearchSource(BaseModel):
    """Cached research source for evidence retrieval."""
    __tablename__ = "research_sources"

    url: Mapped[str] = mapped_column(String(2000), nullable=False, unique=True, index=True)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # scientific | news | regulatory | competitor | social
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    publication_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    retrieved_at: Mapped[str] = mapped_column(String(50), nullable=False)
    content_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    reliability_score: Mapped[float] = mapped_column(Float, default=0.5)  # 0-1
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False)


# Import here to avoid circular — models reference each other
from app.models.content import ContentIdea  # noqa: E402, F401
