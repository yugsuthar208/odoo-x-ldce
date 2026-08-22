import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, Date, DateTime, JSON, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class TransitLeg(Base):
    """Represents a travel journey between two stops or origin and first stop."""
    __tablename__ = "transit_legs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # from_stop_id / origin_stop_id can be null if it's the origin city
    from_stop_id = Column(String(36), ForeignKey("trip_stops.id", ondelete="CASCADE"), nullable=True)
    to_stop_id = Column(String(36), ForeignKey("trip_stops.id", ondelete="CASCADE"), nullable=False)
    
    travel_date = Column(Date, nullable=True)
    selected_option_id = Column(String(36), ForeignKey("transit_options.id", ondelete="SET NULL", use_alter=True, name="fk_transit_leg_selected_option"), nullable=True)
    sequence = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("trip_id", "sequence", name="uq_transit_leg_trip_sequence"),
        CheckConstraint("from_stop_id IS NULL OR from_stop_id != to_stop_id", name="ck_transit_leg_different_stops"),
    )

    trip = relationship("Trip", backref="transit_legs")
    options = relationship(
        "TransitOption", 
        back_populates="leg", 
        cascade="all, delete-orphan", 
        primaryjoin="TransitLeg.id==TransitOption.transit_leg_id"
    )
    selected_option = relationship(
        "TransitOption", 
        primaryjoin="TransitLeg.selected_option_id==TransitOption.id", 
        post_update=True
    )

    @property
    def origin_stop_id(self) -> str:
        return self.from_stop_id

    @origin_stop_id.setter
    def origin_stop_id(self, value: str):
        self.from_stop_id = value

    @property
    def destination_stop_id(self) -> str:
        return self.to_stop_id

    @destination_stop_id.setter
    def destination_stop_id(self, value: str):
        self.to_stop_id = value


class TransitOption(Base):
    """An available or calculated transit option (Train, Flight, Bus, Cab) for a leg."""
    __tablename__ = "transit_options"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    transit_leg_id = Column(String(36), ForeignKey("transit_legs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    mode = Column(String(50), nullable=False)  # flight, train, bus, cab
    provider = Column(String(255), nullable=True)
    label = Column(String(255), nullable=True)
    estimated_duration_minutes = Column(Integer, nullable=True)
    duration_hours = Column(Float, nullable=True)
    
    total_estimated_cost = Column(Float, nullable=False, default=0.0)
    cost_per_person = Column(Float, nullable=False, default=0.0)
    currency = Column(String(10), default="INR", nullable=False)
    metadata_json = Column(JSON, nullable=True)
    source = Column(String(50), default="generated", nullable=True)
    
    is_estimate = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    leg = relationship(
        "TransitLeg", 
        back_populates="options", 
        primaryjoin="TransitOption.transit_leg_id==TransitLeg.id"
    )

