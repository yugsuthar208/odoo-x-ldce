from datetime import date, time
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.activity import ActivityOut


class ItineraryItemBase(BaseModel):
    """Base schema for itinerary items."""
    scheduled_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    custom_cost: Optional[float] = Field(None, ge=0.0)
    notes: Optional[str] = None
    status: str = "planned"  # planned, confirmed, cancelled


class ItineraryItemCreate(BaseModel):
    """Payload for scheduling an activity to a stop."""
    activity_id: str
    scheduled_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    custom_cost: Optional[float] = Field(None, ge=0.0)
    notes: Optional[str] = None
    status: Optional[str] = "planned"


class ItineraryItemUpdate(BaseModel):
    """Payload for modifying an itinerary item."""
    scheduled_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    custom_cost: Optional[float] = Field(None, ge=0.0)
    notes: Optional[str] = None
    status: Optional[str] = None


class ItineraryItemOut(ItineraryItemBase):
    """Response schema for scheduled itinerary item."""
    id: str
    trip_stop_id: str
    activity_id: str
    activity: Optional[ActivityOut] = None

    @property
    def stop_id(self) -> str:
        return self.trip_stop_id

    model_config = ConfigDict(from_attributes=True)


# Backwards compatibility aliases
StopActivityAssign = ItineraryItemCreate
StopActivityOut = ItineraryItemOut


# ============================================================================
# ITINERARY & CONFLICT SCHEMAS
# ============================================================================

class DayItineraryStopGroup(BaseModel):
    """Group of activities for a specific city/stop on a date."""
    stop_id: str
    city_name: str
    activities: List[ItineraryItemOut] = []


class ItineraryDayOut(BaseModel):
    """Day schedule containing date, stop groups, and daily summary."""
    date: str
    stops: List[DayItineraryStopGroup] = []
    day_total_cost: float = 0.0
    day_total_items: int = 0


class ItineraryResponseOut(BaseModel):
    """Full day-wise trip itinerary response."""
    trip_id: str
    trip_title: str
    days: List[ItineraryDayOut] = []
    total_items: int = 0
    total_estimated_cost: float = 0.0


class ConflictItemInfo(BaseModel):
    name: str
    start: str
    end: str


class ConflictDetailOut(BaseModel):
    date: str
    city: str
    item_a: ConflictItemInfo
    item_b: ConflictItemInfo
    overlap_minutes: int


class ConflictResponseOut(BaseModel):
    trip_id: str
    conflicts: List[ConflictDetailOut] = []
    total_conflicts: int = 0


# ============================================================================
# AI ITINERARY GENERATOR SCHEMAS
# ============================================================================

class GenerateItineraryRequest(BaseModel):
    """Payload requesting AI rule-based itinerary generation."""
    interests: List[str] = Field(default_factory=lambda: ["sightseeing", "food"])
    pace: str = Field(default="moderate")  # relaxed (2/day), moderate (3/day), intensive (5/day)
    budget_preference: str = Field(default="mid-range")  # budget (<$20), mid-range ($20-80), luxury (>$80)
    travel_type: str = Field(default="solo")  # solo, couple, family, group


class GeneratedDayActivityOut(BaseModel):
    activity_id: str
    name: str
    start_time: str
    end_time: str
    estimated_cost: float
    category: str


class GeneratedDayOut(BaseModel):
    date: str
    city: str
    activities: List[GeneratedDayActivityOut] = []
    day_total_cost: float
    day_total_hours: float


class GeneratedItineraryOut(BaseModel):
    trip_id: str
    generated_days: List[GeneratedDayOut] = []
    total_activities: int
    estimated_total_cost: float
