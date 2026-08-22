from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.activity_controller import assign_activity_to_stop, remove_activity_from_stop
from app.controllers.stop_controller import delete_stop, update_stop
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.activity import StopActivityAssign, StopActivityOut
from app.schemas.common import APIResponse
from app.schemas.stop import StopOut, StopUpdate

router = APIRouter(prefix="/stops", tags=["Stops & Stop Activities"])


@router.put(
    "/{id}",
    response_model=APIResponse[StopOut],
    status_code=status.HTTP_200_OK,
    summary="Edit stop dates or order index",
)
async def edit_stop(
    id: str,
    payload: StopUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Updates arrival/departure dates or changes the order sequence for a stop.
    """
    stop = await update_stop(db=db, stop_id=id, current_user=current_user, payload=payload)
    return APIResponse(
        success=True,
        data=stop,
        message="Stop updated successfully",
    )


@router.delete(
    "/{id}",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Remove a stop from trip",
)
async def remove_stop(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Removes a stop and all associated scheduled activities from its parent trip.
    """
    result = await delete_stop(db=db, stop_id=id, current_user=current_user)
    return APIResponse(
        success=True,
        data=result,
        message="Stop removed successfully",
    )


@router.post(
    "/{id}/activities",
    response_model=APIResponse[StopActivityOut],
    status_code=status.HTTP_201_CREATED,
    summary="Assign activity to a stop",
)
async def schedule_activity_to_stop(
    id: str,
    payload: StopActivityAssign,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Schedules an activity under the specified stop, with optional date, time, and notes.
    """
    stop_activity = await assign_activity_to_stop(
        db=db, stop_id=id, current_user=current_user, payload=payload
    )
    return APIResponse(
        success=True,
        data=stop_activity,
        message="Activity scheduled to stop successfully",
    )


@router.delete(
    "/{stop_id}/activities/{activity_id}",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Remove activity from a stop",
)
async def unassign_activity_from_stop(
    stop_id: str,
    activity_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Removes a scheduled activity from a stop.
    """
    result = await remove_activity_from_stop(
        db=db, stop_id=stop_id, activity_id=activity_id, current_user=current_user
    )
    return APIResponse(
        success=True,
        data=result,
        message="Activity removed from stop successfully",
    )
