import uuid
from sqlalchemy import Column, String, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Stop(Base):
    """Stop database model representing a city stay within a trip."""
    __tablename__ = "stops"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    city_id = Column(String(36), ForeignKey("cities.id", ondelete="CASCADE"), nullable=False, index=True)
    arrival_date = Column(Date, nullable=False)
    departure_date = Column(Date, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)

    # Relationships
    trip = relationship("Trip", back_populates="stops")
    city = relationship("City", back_populates="stops", lazy="selectin")
    stop_activities = relationship(
        "StopActivity",
        back_populates="stop",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
