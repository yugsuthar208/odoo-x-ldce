import uuid
from datetime import date, datetime
from enum import Enum
from sqlalchemy import Column, String, Text, Date, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class TripStatus(str, Enum):
    DRAFT = "DRAFT"
    PLANNING = "PLANNING"
    READY = "READY"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"


VALID_STATUS_TRANSITIONS = {
    "DRAFT": {"PLANNING", "CANCELLED"},
    "PLANNING": {"READY", "CANCELLED"},
    "READY": {"ACTIVE", "CANCELLED"},
    "ACTIVE": {"COMPLETED", "CANCELLED"},
    "COMPLETED": {"ARCHIVED"},
    "CANCELLED": {"ARCHIVED"},
    "ARCHIVED": set(),
}


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
    origin_city = Column(String(100), default="Mumbai", nullable=True)  # Starting location for transit & route calculation
    num_travelers = Column(Float, default=1, nullable=False)            # Group / Team size
    transit_mode = Column(String(50), default="train", nullable=True)   # preferred mode: flight, train, bus, cab, optimal
    total_budget = Column(Float, nullable=True)                         # Computed / estimated budget
    budget_target = Column(Float, nullable=True)                        # User's target budget limit
    budget_currency = Column(String(10), default="INR", nullable=False) # Currency for target budget
    currency = Column(String(10), default="INR", nullable=False)
    visibility = Column(String(20), default="private", nullable=False)  # private, public
    status = Column(String(20), default="DRAFT", nullable=False)        # DRAFT, PLANNING, READY, ACTIVE, COMPLETED, CANCELLED, ARCHIVED
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

    def can_transition_to(self, new_status: str, admin_override: bool = False) -> bool:
        """Checks if a status transition is allowed."""
        current = self.status.upper()
        target = new_status.upper()

        if current == target:
            return True

        if admin_override:
            return True

        allowed = VALID_STATUS_TRANSITIONS.get(current, set())
        return target in allowed

    def dynamic_status(self) -> str:
        """
        Computes dynamic status according to platform rules.
        Normalizes status to uppercase.
        """
        st = (self.status or "DRAFT").upper()
        if st in ["DRAFT", "PLANNING", "CANCELLED", "ARCHIVED"]:
            return st

        today = date.today()
        if self.start_date > today:
            return st if st == "READY" else "READY"
        elif self.start_date <= today <= self.end_date:
            return "ACTIVE"
        else:
            return "COMPLETED"

