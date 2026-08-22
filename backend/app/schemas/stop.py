from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.city import CityOut
from app.schemas.activity import StopActivityOut


class StopBase(BaseModel):
    """Base schema for trip stops."""
    arrival_date: date
    departure_date: date
    order_index: int = Field(default=0, ge=0)


class StopCreate(StopBase):
    """Payload for adding a stop to a trip."""
    city_id: str


class StopUpdate(BaseModel):
    """Payload for updating stop dates or ordering."""
    arrival_date: Optional[date] = None
    departure_date: Optional[date] = None
    order_index: Optional[int] = Field(None, ge=0)


class StopOut(StopBase):
    """Response schema for a trip stop."""
    id: str
    trip_id: str
    city_id: str
    city: Optional[CityOut] = None
    stop_activities: List[StopActivityOut] = []

    model_config = ConfigDict(from_attributes=True)
