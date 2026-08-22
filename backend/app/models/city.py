import uuid
from sqlalchemy import Column, String, Float, Text
from sqlalchemy.orm import relationship
from app.database import Base


class City(Base):
    """City database model representing global travel destinations."""
    __tablename__ = "cities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(255), nullable=False, index=True)
    country = Column(String(255), nullable=False, index=True)
    region = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)
    cost_index = Column(Float, nullable=False, default=80.0)  # average daily cost in USD
    popularity_score = Column(Float, nullable=False, default=8.0)
    latitude = Column(Float, nullable=True, default=0.0)
    longitude = Column(Float, nullable=True, default=0.0)
    image_url = Column(String(512), nullable=True)

    # Relationships
    activities = relationship("Activity", back_populates="city", cascade="all, delete-orphan", lazy="selectin")
    stops = relationship("TripStop", back_populates="city", lazy="selectin")
    favorites = relationship("Favorite", back_populates="city", cascade="all, delete-orphan", lazy="selectin")
