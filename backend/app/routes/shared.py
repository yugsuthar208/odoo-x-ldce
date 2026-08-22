from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.shared_controller import copy_shared_trip, get_shared_trip
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.shared_link import SharedTripViewOut
from app.schemas.trip import TripDetailOut

router = APIRouter(prefix="/shared", tags=["Shared Links"])


@router.get(
    "/{token}",
    response_model=APIResponse[SharedTripViewOut],
    status_code=status.HTTP_200_OK,
    summary="Get public read-only shared trip",
)
async def view_shared_trip(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Public read-only view of a trip itinerary via share token.
    Conceals private notes and actual expense amounts.
    """
    trip_data = await get_shared_trip(db=db, token=token)
    return APIResponse(
        success=True,
        data=trip_data,
        message="Shared trip retrieved successfully",
    )


@router.post(
    "/{token}/copy",
    response_model=APIResponse[TripDetailOut],
    status_code=status.HTTP_201_CREATED,
    summary="Copy shared trip to user account",
)
async def copy_shared_trip_to_account(
    token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Copies a shared public trip to the authenticated user's account as a new draft."""
    copied_trip = await copy_shared_trip(db=db, token=token, current_user=current_user)
    return APIResponse(
        success=True,
        data=copied_trip,
        message="Shared trip copied to your account as a new draft",
    )
