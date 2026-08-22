import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Trip(Base):
    """Trip database model representing an itinerary planned by a user."""
    __tablename__ = "trips"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    cover_photo = Column(String(512), nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="trips")
    stops = relationship(
        "Stop",
        back_populates="trip",
        cascade="all, delete-orphan",
        order_by="Stop.order_index",
        lazy="selectin"
    )
    budget = relationship(
        "Budget",
        back_populates="trip",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin"
    )
