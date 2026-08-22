from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, model_validator
from app.schemas.city import CityOut
from app.schemas.activity import ActivityOut


class FavoriteCreate(BaseModel):
    """Payload for bookmarking a city or activity."""
    city_id: Optional[str] = None
    activity_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_target(self):
        if not self.city_id and not self.activity_id:
            raise ValueError("At least one of city_id or activity_id must be provided")
        return self


class FavoriteOut(BaseModel):
    """Response schema for favorite entry."""
    id: str
    user_id: str
    city_id: Optional[str] = None
    activity_id: Optional[str] = None
    created_at: datetime
    city: Optional[CityOut] = None
    activity: Optional[ActivityOut] = None

    model_config = ConfigDict(from_attributes=True)
