import uuid
from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Budget(Base):
    """Budget database model representing cost allocations for a trip."""
    __tablename__ = "budgets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    transport_cost = Column(Float, default=0.0, nullable=False)
    stay_cost = Column(Float, default=0.0, nullable=False)
    meals_cost = Column(Float, default=0.0, nullable=False)
    misc_cost = Column(Float, default=0.0, nullable=False)
    total_budget_limit = Column(Float, nullable=True)

    # Relationships
    trip = relationship("Trip", back_populates="budget")
