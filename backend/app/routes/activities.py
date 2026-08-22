from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.activity_controller import create_activity, get_activity
from app.database import get_db
from app.schemas.activity import ActivityCreate, ActivityOut
from app.schemas.common import APIResponse

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get(
    "/{id}",
    response_model=APIResponse[ActivityOut],
    status_code=status.HTTP_200_OK,
    summary="Get single activity by ID",
)
async def get_single_activity(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves full details of an activity."""
    act = await get_activity(db=db, activity_id=id)
    return APIResponse(
        success=True,
        data=act,
        message="Activity retrieved successfully",
    )


@router.post(
    "",
    response_model=APIResponse[ActivityOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new activity",
)
async def add_activity(
    payload: ActivityCreate,
    db: AsyncSession = Depends(get_db),
):
    """Creates a new activity catalog entry for a city."""
    activity = await create_activity(db=db, payload=payload)
    return APIResponse(
        success=True,
        data=activity,
        message="Activity created successfully",
    )
