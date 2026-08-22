import secrets
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class SharedLink(Base):
    """SharedLink database model for secure public shareable trip links."""
    __tablename__ = "shared_links"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    share_token = Column(String(64), unique=True, nullable=False, index=True, default=lambda: secrets.token_urlsafe(16))
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    trip = relationship("Trip", back_populates="shared_links")

    @property
    def is_expired(self) -> bool:
        """Checks if the link has exceeded its expiration timestamp."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
