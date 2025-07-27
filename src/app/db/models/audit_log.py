"""Audit log database model."""

from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from app.db.models.base import Base
from app.db.models.uuid import UUID


class AuditLog(Base):  # type: ignore[misc]  # type: ignore[misc]
    """Audit log model."""

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    request_data = Column(JSON, nullable=True)
    response_status = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    # Indexes
    __table_args__ = (
        Index("idx_audit_user_action", "user_id", "action"),
        Index("idx_audit_created", "created_at"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
        Index("idx_audit_action", "action"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<AuditLog {self.action} by {self.user_id}>"
