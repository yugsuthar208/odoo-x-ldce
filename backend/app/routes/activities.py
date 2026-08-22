from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.activity_controller import create_activity, list_city_activities
from app.database import get_db
from app.schemas.activity import ActivityCreate, ActivityOut
from app.schemas.common import APIResponse

router = APIRouter(prefix="/activities", tags=["Activities"])


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
    """
    Creates a new activity catalog entry for a city.
    """
    activity = await create_activity(db=db, payload=payload)
    return APIResponse(
        success=True,
        data=activity,
        message="Activity created successfully",
    )
