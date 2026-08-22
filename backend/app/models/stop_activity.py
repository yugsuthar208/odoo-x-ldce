import uuid
from sqlalchemy import Column, String, Text, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class StopActivity(Base):
    """StopActivity database model representing an activity scheduled during a stop."""
    __tablename__ = "stop_activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    stop_id = Column(String(36), ForeignKey("stops.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id = Column(String(36), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_date = Column(Date, nullable=True)
    scheduled_time = Column(Time, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    stop = relationship("Stop", back_populates="stop_activities")
    activity = relationship("Activity", back_populates="stop_activities", lazy="selectin")
