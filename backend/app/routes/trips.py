from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.stop_controller import add_stop
from app.controllers.trip_controller import (
    calculate_trip_budget,
    create_trip,
    delete_trip,
    get_public_trip,
    get_trip_detail,
    list_user_trips,
    update_trip,
)
from app.database import get_db
from app.middleware.auth import get_current_user, get_optional_current_user
from app.models.user import User
from app.schemas.budget import BudgetCalculationOut
from app.schemas.common import APIResponse
from app.schemas.stop import StopCreate, StopOut
from app.schemas.trip import PublicTripOut, TripCreate, TripDetailOut, TripOut, TripUpdate

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.get(
    "",
    response_model=APIResponse[List[TripOut]],
    status_code=status.HTTP_200_OK,
    summary="List trips for current user",
)
async def get_my_trips(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns all travel plans created by the authenticated traveler.
    """
    trips = await list_user_trips(db=db, user_id=current_user.id)
    return APIResponse(
        success=True,
        data=trips,
        message="User trips retrieved successfully",
    )


@router.post(
    "",
    response_model=APIResponse[TripDetailOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new trip",
)
async def create_new_trip(
    payload: TripCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a new travel itinerary and initializes its budget configuration.
    """
    trip = await create_trip(db=db, user_id=current_user.id, payload=payload)
    return APIResponse(
        success=True,
        data=trip,
        message="Trip created successfully",
    )


@router.get(
    "/public/{id}",
    response_model=APIResponse[PublicTripOut],
    status_code=status.HTTP_200_OK,
    summary="Get public read-only trip",
)
async def get_public_trip_view(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Public read-only view of a trip itinerary. Requires no authentication.
    """
    trip = await get_public_trip(db=db, trip_id=id)
    return APIResponse(
        success=True,
        data=trip,
        message="Public trip retrieved successfully",
    )


@router.get(
    "/{id}",
    response_model=APIResponse[TripDetailOut],
    status_code=status.HTTP_200_OK,
    summary="Get single trip with stops and budget",
)
async def get_trip(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves full details of a specific trip, including all scheduled stops, activities, and budget allocations.
    """
    trip = await get_trip_detail(db=db, trip_id=id, current_user=current_user)
    return APIResponse(
        success=True,
        data=trip,
        message="Trip retrieved successfully",
    )


@router.put(
    "/{id}",
    response_model=APIResponse[TripDetailOut],
    status_code=status.HTTP_200_OK,
    summary="Update trip details",
)
async def edit_trip(
    id: str,
    payload: TripUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Updates general metadata for an existing trip (title, dates, photo, privacy).
    """
    trip = await update_trip(db=db, trip_id=id, current_user=current_user, payload=payload)
    return APIResponse(
        success=True,
        data=trip,
        message="Trip updated successfully",
    )


@router.delete(
    "/{id}",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete a trip",
)
async def remove_trip(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Permanently deletes a trip, associated stops, and budget data.
    """
    result = await delete_trip(db=db, trip_id=id, current_user=current_user)
    return APIResponse(
        success=True,
        data=result,
        message="Trip deleted successfully",
    )


@router.get(
    "/{id}/budget",
    response_model=APIResponse[BudgetCalculationOut],
    status_code=status.HTTP_200_OK,
    summary="Full cost breakdown for trip",
)
async def get_trip_budget_breakdown(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Computes exact budget breakdown according to upgraded GlobeTrotter rules:
    - stay_cost = SUM of (city.cost_index * days_at_stop)
    - activities_cost = SUM of all stop_activities.activity.cost
    - meals_cost = MEALS_PER_DAY_USD * total_trip_days
    - transport_cost and misc_cost from budgets table
    - total_cost, cost_per_day, savings_needed_per_day
    - budget_status (limit, is_over_budget, budget_overage, budget_remaining)
    - stop_breakdown and cost_distribution_percent
    """
    budget_data = await calculate_trip_budget(trip_id=id, current_user=current_user, db=db)
    return APIResponse(
        success=True,
        data=budget_data,
        message="Budget calculated successfully",
    )


@router.post(
    "/{id}/stops",
    response_model=APIResponse[StopOut],
    status_code=status.HTTP_201_CREATED,
    summary="Add a stop to a trip",
)
async def add_stop_to_trip(
    id: str,
    payload: StopCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Appends a new destination city stay (arrival and departure dates, order index) to the trip.
    """
    stop = await add_stop(db=db, trip_id=id, current_user=current_user, payload=payload)
    return APIResponse(
        success=True,
        data=stop,
        message="Stop added to trip successfully",
    )
