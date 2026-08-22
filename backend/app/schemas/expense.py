from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ExpenseBase(BaseModel):
    """Base schema for trip expenses."""
    category: str = Field(default="misc")  # transport, stay, food, activity, misc
    description: str = Field(..., min_length=1, max_length=255)
    estimated_amount: float = Field(default=0.0, ge=0.0)
    actual_amount: Optional[float] = Field(None, ge=0.0)
    currency: str = "USD"
    paid_by: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    """Payload for logging an expense."""
    pass


class ExpenseUpdate(BaseModel):
    """Payload for modifying an existing expense."""
    category: Optional[str] = None
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    estimated_amount: Optional[float] = Field(None, ge=0.0)
    actual_amount: Optional[float] = Field(None, ge=0.0)
    currency: Optional[str] = None
    paid_by: Optional[str] = None


class ExpenseOut(ExpenseBase):
    """Response schema for expense item."""
    id: str
    trip_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
