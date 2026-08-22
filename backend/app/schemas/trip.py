from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.stop import StopOut
from app.schemas.budget import BudgetOut


class TripBase(BaseModel):
    """Base schema for trip."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: date
    end_date: date
    cover_photo: Optional[str] = None
    is_public: bool = False


class TripCreate(TripBase):
    """Payload for creating a trip."""
    pass


class TripUpdate(BaseModel):
    """Payload for modifying trip details."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    cover_photo: Optional[str] = None
    is_public: Optional[bool] = None


class TripOut(TripBase):
    """Basic trip response."""
    id: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TripDetailOut(TripOut):
    """Comprehensive trip response with stops, activities, and budget."""
    stops: List[StopOut] = []
    budget: Optional[BudgetOut] = None

    model_config = ConfigDict(from_attributes=True)


class PublicTripOut(BaseModel):
    """Public read-only trip overview."""
    id: str
    title: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    cover_photo: Optional[str] = None
    is_public: bool
    created_at: datetime
    stops: List[StopOut] = []

    model_config = ConfigDict(from_attributes=True)
