import uuid
from sqlalchemy import Column, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Activity(Base):
    """Activity database model representing things to do in a city."""
    __tablename__ = "activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    city_id = Column(String(36), ForeignKey("cities.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False, index=True)  # e.g., sightseeing, food, adventure, culture, relaxation
    description = Column(Text, nullable=True)
    cost = Column(Float, default=0.0, nullable=False)  # in USD
    duration_hours = Column(Float, default=1.0, nullable=False)
    image_url = Column(String(512), nullable=True)

    # Relationships
    city = relationship("City", back_populates="activities")
    stop_activities = relationship("StopActivity", back_populates="activity", cascade="all, delete-orphan")
