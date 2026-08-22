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
    search: Optional[str] = Query(None, description="Search by city name, country, or region"),
    region: Optional[str] = Query(None, description="Filter by continent/region (e.g. Europe, Asia)"),
    country: Optional[str] = Query(None, description="Filter by country (e.g. France, Japan)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves destination cities with optional text search, region, and country filters.
    """
    cities = await list_cities(db=db, search=search, region=region, country=country)
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
    "/{city_id}/activities",
    response_model=APIResponse[List[ActivityOut]],
    status_code=status.HTTP_200_OK,
    summary="List activities for a specific city",
)
async def get_city_activity_list(
    city_id: str,
    category: Optional[str] = Query(None, description="Filter by category (sightseeing, food, adventure, shopping, nature, history, wellness)"),
    type: Optional[str] = Query(None, description="Category alias for backwards compatibility"),
    max_cost: Optional[float] = Query(None, ge=0, description="Filter activities costing up to this amount in USD"),
    max_duration: Optional[float] = Query(None, ge=0, description="Filter activities taking up to this duration in hours"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves activities available in a specific city with optional filtering by category, max cost, and duration.
    """
    cat = category or type
    activities = await list_city_activities(
        db=db,
        city_id=city_id,
        category=cat,
        max_cost=max_cost,
        max_duration=max_duration,
    )
    return APIResponse(
        success=True,
        data=activities,
        message="Activities retrieved successfully",
    )
