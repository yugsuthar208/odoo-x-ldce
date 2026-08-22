from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.activity import ActivityOut


class CityBase(BaseModel):
    """Base schema for city destinations."""
    name: str = Field(..., min_length=1, max_length=255)
    country: str = Field(..., min_length=1, max_length=255)
    region: str = Field(..., min_length=1, max_length=255)
    cost_index: float = Field(default=100.0, ge=0.0)
    popularity_score: float = Field(default=50.0, ge=0.0, le=100.0)
    image_url: Optional[str] = None


class CityCreate(CityBase):
    """Payload for creating a city."""
    pass


class CityOut(CityBase):
    """Standard city response schema."""
    id: str

    model_config = ConfigDict(from_attributes=True)


class CityDetailOut(CityOut):
    """City detail schema including available activities."""
    activities: List[ActivityOut] = []

    model_config = ConfigDict(from_attributes=True)
