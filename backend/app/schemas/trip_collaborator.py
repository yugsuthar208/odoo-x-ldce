from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from app.schemas.user import UserOut


class CollaboratorAddRequest(BaseModel):
    """Payload for inviting a collaborator to a trip."""
    email: EmailStr
    role: str = Field(default="editor")  # editor, viewer


class CollaboratorOut(BaseModel):
    """Response schema for collaborator."""
    id: str
    trip_id: str
    user_id: str
    role: str
    joined_at: datetime
    user: Optional[UserOut] = None

    model_config = ConfigDict(from_attributes=True)
