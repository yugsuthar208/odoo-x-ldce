from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.itinerary_controller import (
    delete_itinerary_item,
    update_itinerary_item,
)
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.itinerary_item import ItineraryItemOut, ItineraryItemUpdate

router = APIRouter(prefix="/itinerary-items", tags=["Itinerary Items"])


@router.put(
    "/{item_id}",
    response_model=APIResponse[ItineraryItemOut],
    status_code=status.HTTP_200_OK,
    summary="Edit scheduled itinerary item",
)
async def edit_itinerary_item(
    item_id: str,
    payload: ItineraryItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Modifies scheduled date, start/end time, custom cost, notes, or status."""
    item = await update_itinerary_item(db=db, item_id=item_id, current_user=current_user, payload=payload)
    return APIResponse(
        success=True,
        data=item,
        message="Itinerary item updated successfully",
    )


@router.delete(
    "/{item_id}",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete scheduled itinerary item",
)
async def remove_itinerary_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deletes an item from the itinerary."""
    result = await delete_itinerary_item(db=db, item_id=item_id, current_user=current_user)
    return APIResponse(
        success=True,
        data=result,
        message="Itinerary item removed successfully",
    )
