from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class ActivityBase(BaseModel):
    """Base schema for activity."""
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(default="sightseeing", min_length=1, max_length=100)
    description: Optional[str] = None
    estimated_cost: float = Field(default=0.0, ge=0.0)
    duration_hours: float = Field(default=1.0, gt=0.0)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    tags: List[str] = []
    vibe: Optional[str] = "relaxing"
    best_for: List[str] = []

    @property
    def cost(self) -> float:
        return self.estimated_cost

    @property
    def type(self) -> str:
        return self.category


class ActivityCreate(BaseModel):
    """Payload for creating a new activity."""
    city_id: str
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(default="sightseeing", min_length=1, max_length=100)
    description: Optional[str] = None
    estimated_cost: float = Field(default=0.0, ge=0.0)
    duration_hours: float = Field(default=1.0, gt=0.0)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    tags: List[str] = []
    vibe: Optional[str] = "relaxing"
    best_for: List[str] = []


class ActivityOut(ActivityBase):
    """Response schema for activity."""
    id: str
    city_id: str

    model_config = ConfigDict(from_attributes=True)
