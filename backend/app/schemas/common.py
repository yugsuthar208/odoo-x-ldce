from typing import Generic, Optional, TypeVar, Any
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standardized API success response wrapper."""
    success: bool = True
    data: Optional[T] = None
    message: str = "Operation successful"

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Standardized API error response wrapper."""
    success: bool = False
    error: str
    status_code: int

    model_config = ConfigDict(from_attributes=True)
