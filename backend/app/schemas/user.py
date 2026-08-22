from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field, model_validator


class UserBase(BaseModel):
    """Base user fields."""
    name: Optional[str] = None
    full_name: Optional[str] = None
    email: EmailStr
    profile_photo: Optional[str] = None
    preferred_currency: str = "USD"
    language: str = "en"

    @model_validator(mode="before")
    @classmethod
    def resolve_name(cls, values):
        if isinstance(values, dict):
            if not values.get("name") and values.get("full_name"):
                values["name"] = values["full_name"]
            elif not values.get("full_name") and values.get("name"):
                values["full_name"] = values["name"]
        return values


class UserCreate(BaseModel):
    """Payload for user registration."""
    name: Optional[str] = None
    full_name: Optional[str] = None
    email: EmailStr
    password: str = Field(..., min_length=6)
    profile_photo: Optional[str] = None
    preferred_currency: Optional[str] = "USD"
    language: Optional[str] = "en"

    @model_validator(mode="before")
    @classmethod
    def resolve_name(cls, values):
        if isinstance(values, dict):
            val = values.get("name") or values.get("full_name")
            if not val:
                raise ValueError("Name or full_name is required")
            values["name"] = val
            values["full_name"] = val
        return values


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
    full_name: Optional[str] = None
    profile_photo: Optional[str] = None
    preferred_currency: Optional[str] = None
    language: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def resolve_name(cls, values):
        if isinstance(values, dict):
            if not values.get("name") and values.get("full_name"):
                values["name"] = values["full_name"]
            elif not values.get("full_name") and values.get("name"):
                values["full_name"] = values["name"]
        return values


class UserOut(BaseModel):
    """User response schema."""
    id: str
    name: str
    full_name: Optional[str] = None
    email: str
    profile_photo: Optional[str] = None
    preferred_currency: str = "USD"
    language: str = "en"
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def resolve_full_name(cls, data):
        if hasattr(data, "name") and not getattr(data, "full_name", None):
            data.full_name = data.name
        elif isinstance(data, dict):
            if not data.get("full_name") and data.get("name"):
                data["full_name"] = data["name"]
        return data

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """JWT Token response schema."""
    access_token: str
    token_type: str = "bearer"
    user: UserOut
