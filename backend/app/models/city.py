import uuid
from sqlalchemy import Column, String, Float, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class City(Base):
    """City database model representing global travel destinations with rich tags and vibes."""
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

    # ML & Vibe Attributes
    tags = Column(JSON, default=list, nullable=False)            # e.g. ["romantic", "fashion", "art"]
    vibe_tags = Column(JSON, default=list, nullable=False)       # e.g. ["vibrant", "cultural", "luxurious"]
    climate_type = Column(String(50), default="temperate")       # tropical, mediterranean, continental, arid, oceanic
    best_months = Column(JSON, default=list, nullable=False)     # e.g. ["April", "May", "September"]
    safety_index = Column(Float, default=75.0, nullable=False)   # 0 to 100
    budget_tier = Column(String(20), default="mid-range")        # budget, mid-range, luxury
    rent_index = Column(Float, default=50.0, nullable=False)
    restaurant_price_index = Column(Float, default=60.0, nullable=False)

    # Relationships
    activities = relationship("Activity", back_populates="city", cascade="all, delete-orphan", lazy="selectin")
    stops = relationship("TripStop", back_populates="city", lazy="selectin")
    favorites = relationship("Favorite", back_populates="city", cascade="all, delete-orphan", lazy="selectin")
