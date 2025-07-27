"""Login attempt database model."""

from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.models.base import Base


class LoginAttempt(Base):
    """Login attempt model."""

    __tablename__ = "login_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), nullable=False)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(500), nullable=True)
    success = Column(Boolean, nullable=False)
    attempted_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="login_attempts")

    # Indexes
    __table_args__ = (
        Index("idx_login_attempts_email", "email"),
        Index("idx_login_attempts_ip", "ip_address"),
        Index("idx_login_attempts_time", "attempted_at"),
        Index("idx_login_attempts_email_ip", "email", "ip_address"),
        Index("idx_login_attempts_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<LoginAttempt {self.email} - {'Success' if self.success else 'Failed'}>"
        )
