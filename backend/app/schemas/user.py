from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserBase(BaseModel):
    """Base user fields."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    profile_photo: Optional[str] = None
    language: str = "en"


class UserCreate(BaseModel):
    """Payload for user registration."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6)
    profile_photo: Optional[str] = None
    language: Optional[str] = "en"


class UserLogin(BaseModel):
    """Payload for user login."""
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    """Payload for forgot-password reset token request."""
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """Response payload with generated password reset token."""
    reset_token: str
    message: str


class UserUpdate(BaseModel):
    """Payload for updating user profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    profile_photo: Optional[str] = None
    language: Optional[str] = None


class UserOut(BaseModel):
    """User response schema."""
    id: str
    name: str
    email: str
    profile_photo: Optional[str] = None
    language: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """JWT Token response schema."""
    access_token: str
    token_type: str = "bearer"
    user: UserOut
