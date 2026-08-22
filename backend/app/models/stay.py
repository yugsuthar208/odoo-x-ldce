import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Date, Boolean, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Stay(Base):
    """Catalog of available stays (hotels, hostels, etc.)."""
    __tablename__ = "stays"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    city_id = Column(String(36), ForeignKey("cities.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    provider = Column(String(100), nullable=True)
    source = Column(String(50), default="database", nullable=True)  # e.g., 'duckduckgo', 'database'
    url = Column(String(512), nullable=True)
    estimated_nightly_rate = Column(Float, nullable=True)
    currency = Column(String(10), default="INR", nullable=False)
    metadata_json = Column(JSON, nullable=True)
    is_estimate = Column(Boolean, default=True)
    retrieved_at = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    city = relationship("City")

    @property
    def estimated_nightly_cost(self) -> float:
        return self.estimated_nightly_rate

    @estimated_nightly_cost.setter
    def estimated_nightly_cost(self, val: float):
        self.estimated_nightly_rate = val


class TripStay(Base):
    """A user's selected stay for a specific trip stop."""
    __tablename__ = "trip_stays"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=True, index=True)
    trip_stop_id = Column(String(36), ForeignKey("trip_stops.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    stay_id = Column(String(36), ForeignKey("stays.id", ondelete="SET NULL"), nullable=True)
    
    name = Column(String(255), nullable=False) # Fallback if stay_id is null
    checkin_date = Column(Date, nullable=False)
    checkout_date = Column(Date, nullable=False)
    nightly_cost = Column(Float, nullable=False, default=0.0)
    cost = Column(Float, nullable=False, default=0.0)  # total cost
    currency = Column(String(10), default="INR", nullable=False)
    is_estimate = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    trip_stop = relationship("TripStop", backref="stay_info")
    stay = relationship("Stay")

    @property
    def check_in(self) -> Date:
        return self.checkin_date

    @check_in.setter
    def check_in(self, val: Date):
        self.checkin_date = val

    @property
    def check_out(self) -> Date:
        return self.checkout_date

    @check_out.setter
    def check_out(self, val: Date):
        self.checkout_date = val

    @property
    def total_cost(self) -> float:
        return self.cost

    @total_cost.setter
    def total_cost(self, val: float):
        self.cost = val

