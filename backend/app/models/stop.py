import uuid
from sqlalchemy import Column, String, Date, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class TripStop(Base):
    """TripStop database model representing a scheduled stop in a city."""
    __tablename__ = "trip_stops"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    city_id = Column(String(36), ForeignKey("cities.id", ondelete="CASCADE"), nullable=False, index=True)
    arrival_date = Column(Date, nullable=False)
    departure_date = Column(Date, nullable=False)
    stop_order = Column(Integer, default=0, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    trip = relationship("Trip", back_populates="stops")
    city = relationship("City", back_populates="stops", lazy="selectin")
    itinerary_items = relationship(
        "ItineraryItem",
        back_populates="trip_stop",
        cascade="all, delete-orphan",
        order_by="ItineraryItem.start_time",
        lazy="selectin",
    )

    @property
    def order_index(self) -> int:
        """Alias for stop_order for backwards compatibility."""
        return self.stop_order

    @order_index.setter
    def order_index(self, value: int):
        self.stop_order = value

    @property
    def stop_activities(self):
        """Backwards compatibility alias for itinerary_items."""
        return self.itinerary_items


# Alias for backwards compatibility
Stop = TripStop
