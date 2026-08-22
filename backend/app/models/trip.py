import uuid
from datetime import date, datetime
from sqlalchemy import Column, String, Text, Date, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Trip(Base):
    """Trip database model representing multi-city travel itineraries."""
    __tablename__ = "trips"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    cover_photo = Column(String(512), nullable=True)
    total_budget = Column(Float, nullable=True)
    currency = Column(String(10), default="USD", nullable=False)
    visibility = Column(String(20), default="private", nullable=False)  # private, public, friends
    status = Column(String(20), default="draft", nullable=False)        # draft, upcoming, ongoing, completed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="trips")
    stops = relationship(
        "TripStop",
        back_populates="trip",
        cascade="all, delete-orphan",
        order_by="TripStop.stop_order",
        lazy="selectin",
    )
    budget = relationship(
        "Budget",
        back_populates="trip",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    expenses = relationship(
        "Expense",
        back_populates="trip",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    shared_links = relationship(
        "SharedLink",
        back_populates="trip",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    collaborators = relationship(
        "TripCollaborator",
        back_populates="trip",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def is_public(self) -> bool:
        """Helper property indicating public visibility."""
        return self.visibility == "public"

    def dynamic_status(self) -> str:
        """
        Computes dynamic status according to platform rules:
        - draft stays draft unless published
        - if not draft: upcoming (start > today), ongoing (start <= today <= end), completed (end < today)
        """
        if self.status == "draft":
            return "draft"
        today = date.today()
        if self.start_date > today:
            return "upcoming"
        elif self.start_date <= today <= self.end_date:
            return "ongoing"
        else:
            return "completed"
