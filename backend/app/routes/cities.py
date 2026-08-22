from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.activity_controller import list_city_activities
from app.controllers.city_controller import get_city, list_cities
from app.database import get_db
from app.schemas.activity import ActivityOut
from app.schemas.city import CityDetailOut, CityOut
from app.schemas.common import APIResponse

router = APIRouter(prefix="/cities", tags=["Cities"])


@router.get(
    "",
    response_model=APIResponse[List[CityOut]],
    status_code=status.HTTP_200_OK,
    summary="Search and list cities",
)
async def get_all_cities(
    search: Optional[str] = Query(None, description="Search by city name or country"),
    region: Optional[str] = Query(None, description="Filter by continent/region (e.g. Europe, Asia)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves destination cities with optional full-text search and region filtering.
    """
    cities = await list_cities(db=db, search=search, region=region)
    return APIResponse(
        success=True,
        data=cities,
        message="Cities retrieved successfully",
    )


@router.get(
    "/{id}",
    response_model=APIResponse[CityDetailOut],
    status_code=status.HTTP_200_OK,
    summary="Get city details with activities",
)
async def get_city_details(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves complete details for a single city including its catalog of activities.
    """
    city = await get_city(db=db, city_id=id)
    return APIResponse(
        success=True,
        data=city,
        message="City details retrieved successfully",
    )


@router.get(
    "/{id}/activities",
    response_model=APIResponse[List[ActivityOut]],
    status_code=status.HTTP_200_OK,
    summary="List activities for a specific city",
)
async def get_city_activity_list(
    id: str,
    type: Optional[str] = Query(None, description="Filter by activity category (sightseeing, food, adventure)"),
    max_cost: Optional[float] = Query(None, ge=0, description="Filter activities costing up to this amount in USD"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves activities available in a specific city with optional filtering by type and maximum budget.
    """
    activities = await list_city_activities(db=db, city_id=id, activity_type=type, max_cost=max_cost)
    return APIResponse(
        success=True,
        data=activities,
        message="Activities retrieved successfully",
    )
