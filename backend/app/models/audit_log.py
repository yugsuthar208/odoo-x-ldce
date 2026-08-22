import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class AuditLog(Base):
    """AuditLog database model representing an immutable audit trail of system events."""
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # e.g., 'TRIP_CREATED', 'EXPENSE_DELETED', 'ROLE_UPDATED'
    resource_type = Column(String(50), nullable=False)  # 'trip', 'stop', 'expense', 'collaborator'
    resource_id = Column(String(36), nullable=True)
    details = Column(JSON, nullable=True)  # Structured payload describing the diff / action parameters
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User")
    trip = relationship("Trip")
