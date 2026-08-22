from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.city import CityOut


class SharedLinkCreate(BaseModel):
    """Payload for generating a public shareable link."""
    expires_in_days: Optional[int] = Field(default=7, ge=1, le=365)


class SharedLinkOut(BaseModel):
    """Response schema for share token."""
    id: str
    trip_id: str
    share_token: str
    expires_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SharedActivityOut(BaseModel):
    activity_id: str
    name: str
    category: str
    duration_hours: float
    estimated_cost: float
    scheduled_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class SharedStopOut(BaseModel):
    stop_id: str
    city: CityOut
    arrival_date: date
    departure_date: date
    stop_order: int
    activities: List[SharedActivityOut] = []


class SharedTripViewOut(BaseModel):
    """Sanitized public view of shared trip."""
    trip_id: str
    title: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    cover_photo: Optional[str] = None
    stops: List[SharedStopOut] = []
    total_days: int

    model_config = ConfigDict(from_attributes=True)
