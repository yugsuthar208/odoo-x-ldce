import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Favorite(Base):
    """Favorite database model for saved destination cities and activities."""
    __tablename__ = "favorites"
    __table_args__ = (
        CheckConstraint("city_id IS NOT NULL OR activity_id IS NOT NULL", name="check_favorite_target"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    city_id = Column(String(36), ForeignKey("cities.id", ondelete="CASCADE"), nullable=True, index=True)
    activity_id = Column(String(36), ForeignKey("activities.id", ondelete="CASCADE"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="favorites")
    city = relationship("City", back_populates="favorites", lazy="selectin")
    activity = relationship("Activity", back_populates="favorites", lazy="selectin")
