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
    origin_city: Optional[str] = "Mumbai"
    num_travelers: Optional[float] = 1
    transit_mode: Optional[str] = "train"
    total_budget: Optional[float] = Field(None, ge=0.0)
    currency: str = "INR"
    visibility: str = "private"  # private, public, friends
    status: str = "draft"        # draft, upcoming, ongoing, completed

    @property
    def is_public(self) -> bool:
        return self.visibility == "public"


class TripCreate(BaseModel):
    """Payload for creating a trip."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: date
    end_date: date
    cover_photo: Optional[str] = None
    origin_city: Optional[str] = "Mumbai"
    num_travelers: Optional[float] = 1
    transit_mode: Optional[str] = "train"
    total_budget: Optional[float] = Field(None, ge=0.0)
    currency: Optional[str] = "INR"
    visibility: Optional[str] = "private"
    status: Optional[str] = "draft"
    is_public: Optional[bool] = None  # alias for visibility="public"


class TripUpdate(BaseModel):
    """Payload for modifying trip details."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    cover_photo: Optional[str] = None
    origin_city: Optional[str] = None
    num_travelers: Optional[float] = None
    transit_mode: Optional[str] = None
    total_budget: Optional[float] = Field(None, ge=0.0)
    currency: Optional[str] = None
    visibility: Optional[str] = None
    status: Optional[str] = None
    is_public: Optional[bool] = None


class TripOut(BaseModel):
    """Basic trip response."""
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    cover_photo: Optional[str] = None
    origin_city: Optional[str] = "Mumbai"
    num_travelers: Optional[float] = 1
    transit_mode: Optional[str] = "train"
    total_budget: Optional[float] = None
    currency: str = "INR"
    visibility: str = "private"
    status: str = "draft"
    created_at: datetime

    @property
    def is_public(self) -> bool:
        return self.visibility == "public"

    model_config = ConfigDict(from_attributes=True)


class TripDetailOut(TripOut):
    """Comprehensive trip response with stops and budget."""
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
    visibility: str = "public"
    status: str = "upcoming"
    created_at: datetime
    stops: List[StopOut] = []

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# MAP ROUTE SCHEMAS
# ============================================================================

class MapRouteStopOut(BaseModel):
    stop_order: int
    city_name: str
    country: str
    latitude: float
    longitude: float
    arrival_date: date
    departure_date: date
    days: int


class MapRouteOut(BaseModel):
    trip_id: str
    route: List[MapRouteStopOut] = []
    total_cities: int
    total_distance_km: float
