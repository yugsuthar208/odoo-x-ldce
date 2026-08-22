from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.city import CityOut
from app.schemas.itinerary_item import ItineraryItemOut


class StopBase(BaseModel):
    """Base schema for trip stops."""
    arrival_date: date
    departure_date: date
    stop_order: int = Field(default=0, ge=0)
    notes: Optional[str] = None

    @property
    def order_index(self) -> int:
        return self.stop_order


class StopCreate(BaseModel):
    """Payload for adding a stop to a trip."""
    city_id: str
    arrival_date: date
    departure_date: date
    stop_order: Optional[int] = Field(default=0, ge=0)
    order_index: Optional[int] = Field(default=None, ge=0)  # alias support
    notes: Optional[str] = None


class StopUpdate(BaseModel):
    """Payload for updating stop dates, order, or notes."""
    arrival_date: Optional[date] = None
    departure_date: Optional[date] = None
    stop_order: Optional[int] = Field(None, ge=0)
    order_index: Optional[int] = Field(None, ge=0)  # alias support
    notes: Optional[str] = None


class StopReorderItem(BaseModel):
    """Item specification for batch reordering stops."""
    stop_id: str
    order_index: Optional[int] = None
    stop_order: Optional[int] = None

    def get_order(self) -> int:
        if self.stop_order is not None:
            return self.stop_order
        if self.order_index is not None:
            return self.order_index
        return 0


class StopOut(StopBase):
    """Response schema for a trip stop."""
    id: str
    trip_id: str
    city_id: str
    city: Optional[CityOut] = None
    itinerary_items: List[ItineraryItemOut] = []

    @property
    def stop_activities(self):
        return self.itinerary_items

    model_config = ConfigDict(from_attributes=True)
