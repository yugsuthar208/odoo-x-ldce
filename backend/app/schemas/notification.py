from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict


class NotificationBase(BaseModel):
    """Base schema for user notifications."""
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""
    user_id: str


class NotificationResponse(NotificationBase):
    """Schema for returning a notification to the client."""
    id: str
    user_id: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationUpdate(BaseModel):
    """Schema for marking a notification as read."""
    is_read: bool = True
