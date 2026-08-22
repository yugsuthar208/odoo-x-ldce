import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """User database model representing registered platform travelers."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    profile_photo = Column(String(512), nullable=True)
    preferred_currency = Column(String(10), default="USD", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Convenience properties / aliases
    @property
    def full_name(self) -> str:
        return self.name

    @property
    def avatar_url(self) -> str:
        return self.profile_photo

    # Relationships
    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    collaborations = relationship("TripCollaborator", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    expenses_paid = relationship("Expense", back_populates="paid_by_user", lazy="selectin")
