"""
User and Auth Models — Users, roles, permissions, organizations.
"""
import uuid
from enum import Enum as PyEnum

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class UserRole(str, PyEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MEDICAL_REVIEWER = "medical_reviewer"
    CONTENT_MANAGER = "content_manager"
    ANALYST = "analyst"
    VIEWER = "viewer"


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        String(50), default=UserRole.VIEWER, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ── Relationships ──────────────────────────────────────────────
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    audit_events: Mapped[list["AuditEvent"]] = relationship(back_populates="user")

    def has_role(self, *roles: UserRole) -> bool:
        return self.role in roles

    def can_approve_medical(self) -> bool:
        return self.role in (UserRole.SUPER_ADMIN, UserRole.MEDICAL_REVIEWER)

    def can_manage_content(self) -> bool:
        return self.role in (
            UserRole.SUPER_ADMIN,
            UserRole.ADMIN,
            UserRole.CONTENT_MANAGER,
            UserRole.MEDICAL_REVIEWER,
        )


class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[str] = mapped_column(String(50), nullable=False)  # ISO datetime str
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")


class AuditEvent(BaseModel):
    __tablename__ = "audit_events"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    user: Mapped["User | None"] = relationship(back_populates="audit_events")
