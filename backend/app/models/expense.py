import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Expense(Base):
    """Expense database model representing planned and actual trip expenses."""
    __tablename__ = "expenses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # transport, stay, food, activity, misc
    description = Column(String(255), nullable=False)
    estimated_amount = Column(Float, nullable=False, default=0.0)
    actual_amount = Column(Float, nullable=True)
    currency = Column(String(10), default="USD", nullable=False)
    paid_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    trip = relationship("Trip", back_populates="expenses")
    paid_by_user = relationship("User", back_populates="expenses_paid", lazy="selectin")
