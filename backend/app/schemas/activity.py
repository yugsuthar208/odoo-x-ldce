from datetime import date, time
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ActivityBase(BaseModel):
    """Base schema for activity."""
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    cost: float = Field(default=0.0, ge=0.0)
    duration_hours: float = Field(default=1.0, gt=0.0)
    image_url: Optional[str] = None


class ActivityCreate(ActivityBase):
    """Payload for creating a new activity in a city."""
    city_id: str


class ActivityOut(ActivityBase):
    """Response schema for activity."""
    id: str
    city_id: str

    model_config = ConfigDict(from_attributes=True)


class StopActivityAssign(BaseModel):
    """Payload for assigning an activity to a stop."""
    activity_id: str
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    notes: Optional[str] = None


class StopActivityOut(BaseModel):
    """Response schema for scheduled stop activity."""
    id: str
    stop_id: str
    activity_id: str
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    notes: Optional[str] = None
    activity: Optional[ActivityOut] = None

    model_config = ConfigDict(from_attributes=True)
