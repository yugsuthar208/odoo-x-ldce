import uuid
from sqlalchemy import Column, String, Text, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Activity(Base):
    """Activity database model representing points of interest and experiences."""
    __tablename__ = "activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    city_id = Column(String(36), ForeignKey("cities.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)  # sightseeing, food, adventure, shopping, nature, history, wellness
    description = Column(Text, nullable=True)
    estimated_cost = Column(Float, default=0.0, nullable=False)
    duration_hours = Column(Float, default=1.0, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    image_url = Column(String(512), nullable=True)

    # ML & Vibe Attributes
    tags = Column(JSON, default=list, nullable=False)       # e.g. ["outdoor", "cultural", "foodie"]
    vibe = Column(String(50), default="relaxing")           # thrilling, relaxing, immersive, iconic
    best_for = Column(JSON, default=list, nullable=False)   # e.g. ["solo", "couple", "family", "group"]

    # Relationships
    city = relationship("City", back_populates="activities")
    itinerary_items = relationship("ItineraryItem", back_populates="activity", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="activity", cascade="all, delete-orphan")

    @property
    def cost(self) -> float:
        return self.estimated_cost

    @cost.setter
    def cost(self, val: float):
        self.estimated_cost = val

    @property
    def type(self) -> str:
        return self.category

    @type.setter
    def type(self, val: str):
        self.category = val
