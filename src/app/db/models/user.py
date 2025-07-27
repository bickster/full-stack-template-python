"""User database model."""

from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Index, String
from sqlalchemy.orm import relationship

from app.db.models.base import Base
from app.db.models.uuid import UUID


class User(Base):  # type: ignore[misc]  # type: ignore[misc]
    """User model."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    login_attempts = relationship(
        "LoginAttempt",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Indexes
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_username", "username"),
        Index("idx_users_is_active", "is_active"),
        Index("idx_users_deleted_at", "deleted_at"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<User {self.username}>"

    @property
    def is_deleted(self) -> bool:
        """Check if user is deleted."""
        return self.deleted_at is not None
