import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class TripCollaborator(Base):
    """TripCollaborator database model representing shared access permissions."""
    __tablename__ = "trip_collaborators"
    __table_args__ = (
        UniqueConstraint("trip_id", "user_id", name="uq_trip_collaborator"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), default="editor", nullable=False)  # editor, viewer
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    trip = relationship("Trip", back_populates="collaborators")
    user = relationship("User", back_populates="collaborations", lazy="selectin")
