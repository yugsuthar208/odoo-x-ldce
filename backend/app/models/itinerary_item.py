import uuid
from sqlalchemy import Column, String, Text, Date, Time, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ItineraryItem(Base):
    """ItineraryItem database model representing a scheduled activity under a trip stop."""
    __tablename__ = "itinerary_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    trip_stop_id = Column(String(36), ForeignKey("trip_stops.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id = Column(String(36), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_date = Column(Date, nullable=True, index=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    custom_cost = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default="planned", nullable=False)  # planned, confirmed, cancelled

    # Relationships
    trip_stop = relationship("TripStop", back_populates="itinerary_items")
    activity = relationship("Activity", back_populates="itinerary_items", lazy="selectin")

    @property
    def stop_id(self) -> str:
        """Alias for trip_stop_id."""
        return self.trip_stop_id

    @stop_id.setter
    def stop_id(self, val: str):
        self.trip_stop_id = val

    @property
    def effective_cost(self) -> float:
        """Returns custom_cost if set, otherwise activity.estimated_cost or 0.0."""
        if self.custom_cost is not None:
            return float(self.custom_cost)
        if self.activity and self.activity.estimated_cost is not None:
            return float(self.activity.estimated_cost)
        return 0.0


# Backward compatibility alias
StopActivity = ItineraryItem
