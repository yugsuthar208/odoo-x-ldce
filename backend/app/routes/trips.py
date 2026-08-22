from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.budget_controller import update_trip_budget_settings
from app.controllers.collaborator_controller import (
    add_collaborator,
    list_collaborators,
    remove_collaborator,
)
from app.controllers.expense_controller import create_expense, list_trip_expenses
from app.controllers.itinerary_controller import get_trip_conflicts, get_trip_itinerary
from app.controllers.shared_controller import create_shared_link
from app.controllers.stop_controller import add_stop, delete_stop, reorder_stops, update_stop
from app.controllers.trip_controller import (
    calculate_map_route,
    calculate_trip_budget,
    create_trip,
    delete_trip,
    duplicate_trip,
    get_public_trip,
    get_trip_detail,
    list_user_trips,
    update_trip,
)
from app.database import get_db
from app.middleware.auth import get_current_user, get_optional_current_user
from app.ml.itinerary_generator import generate_ai_itinerary
from app.models.user import User
from app.schemas.budget import BudgetCalculationOut, BudgetUpdate
from app.schemas.common import APIResponse
from app.schemas.expense import ExpenseCreate, ExpenseOut
from app.schemas.itinerary_item import (
    ConflictResponseOut,
    GeneratedItineraryOut,
    GenerateItineraryRequest,
    ItineraryResponseOut,
)
from app.schemas.shared_link import SharedLinkCreate, SharedLinkOut
from app.schemas.stop import StopCreate, StopOut, StopReorderItem, StopUpdate
from app.schemas.trip import (
    MapRouteOut,
    PublicTripOut,
    TripCreate,
    TripDetailOut,
    TripOut,
    TripUpdate,
)
from app.schemas.trip_collaborator import CollaboratorAddRequest, CollaboratorOut

router = APIRouter(prefix="/trips", tags=["Trips & Itineraries"])


@router.get(
    "",
    response_model=APIResponse[List[TripOut]],
    status_code=status.HTTP_200_OK,
    summary="List all trips for current user",
)
async def get_my_trips(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: draft, upcoming, ongoing, completed"),
    search: Optional[str] = Query(None, description="Search in trip title or description"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns all trips where traveler is owner or collaborator."""
    trips = await list_user_trips(db=db, user_id=current_user.id, status_filter=status_filter, search=search)
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
    """Creates a new travel itinerary and initializes its budget configuration."""
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
    """Public read-only view of a trip itinerary."""
    trip = await get_public_trip(db=db, trip_id=id)
    return APIResponse(
        success=True,
        data=trip,
        message="Public trip retrieved successfully",
    )


@router.get(
    "/{id}",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Get single trip with complete workspace state",
)
async def get_trip(
    id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves full trip workspace including transit, stays, activities, and budget."""
    trip = await get_trip_detail(db=db, trip_id=id, current_user=current_user)
    
    from app.services.budget_service import BudgetService
    budget = await BudgetService.calculate_authoritative_budget(db, id)
    
    # Refresh trip to get relationships if needed
    await db.refresh(trip, ["stops", "transit_legs"])
    
    return APIResponse(
        success=True,
        data={
            "trip": {
                "id": trip.id,
                "title": trip.title,
                "description": trip.description,
                "start_date": trip.start_date,
                "end_date": trip.end_date,
                "origin_city": trip.origin_city,
                "num_travelers": trip.num_travelers,
                "currency": trip.currency,
                "status": trip.dynamic_status(),
                "budget_target": trip.budget_target,
            },
            "stops": [{"id": s.id, "city_id": s.city_id, "city_name": s.city.name if s.city else None, "arrival_date": s.arrival_date, "departure_date": s.departure_date, "stop_order": s.stop_order} for s in sorted(trip.stops, key=lambda x: x.stop_order)],
            "transit_legs": [{
                "id": leg.id,
                "sequence": leg.sequence,
                "from_stop_id": leg.from_stop_id,
                "to_stop_id": leg.to_stop_id,
                "selected_option_id": leg.selected_option_id,
                "options": [
                    {
                        "id": opt.id,
                        "mode": opt.mode,
                        "provider": opt.provider,
                        "duration_hours": opt.duration_hours,
                        "total_estimated_cost": opt.total_estimated_cost,
                        "cost_per_person": opt.cost_per_person,
                    } for opt in leg.options
                ]
            } for leg in sorted(trip.transit_legs, key=lambda x: x.sequence)],
            "budget": budget,
        },
        message="Trip detail retrieved successfully",
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
    """Updates general metadata for an existing trip."""
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
    """Permanently deletes a trip (owner only) cascading all related entities."""
    result = await delete_trip(db=db, trip_id=id, current_user=current_user)
    return APIResponse(
        success=True,
        data=result,
        message="Trip deleted successfully",
    )


@router.post(
    "/{id}/duplicate",
    response_model=APIResponse[TripDetailOut],
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate a trip",
)
async def copy_trip(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Copies entire trip including stops, items, and budget configuration as a new draft."""
    cloned_trip = await duplicate_trip(db=db, trip_id=id, current_user=current_user)
    return APIResponse(
        success=True,
        data=cloned_trip,
        message="Trip duplicated successfully as a new draft",
    )


# ============================================================================
# TRIP STOPS SUB-ROUTES
# ============================================================================

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
    """Appends a new destination city stop to the trip."""
    stop = await add_stop(db=db, trip_id=id, current_user=current_user, payload=payload)
    return APIResponse(
        success=True,
        data=stop,
        message="Stop added to trip successfully",
    )


@router.put(
    "/{id}/stops/reorder",
    response_model=APIResponse[List[StopOut]],
    status_code=status.HTTP_200_OK,
    summary="Reorder all stops in trip",
)
async def reorder_trip_stops(
    id: str,
    items: List[StopReorderItem],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Batch updates the sequence order for all stops in a trip."""
    stops = await reorder_stops(db=db, trip_id=id, current_user=current_user, items=items)
    return APIResponse(
        success=True,
        data=stops,
        message="Stops reordered successfully",
    )


@router.put(
    "/{id}/stops/{stop_id}",
    response_model=APIResponse[StopOut],
    status_code=status.HTTP_200_OK,
    summary="Edit stop dates, notes, or order",
)
async def edit_trip_stop(
    id: str,
    stop_id: str,
    payload: StopUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates stop dates, notes, or order."""
    stop = await update_stop(db=db, stop_id=stop_id, current_user=current_user, payload=payload, trip_id=id)
    return APIResponse(
        success=True,
        data=stop,
        message="Stop updated successfully",
    )


@router.delete(
    "/{id}/stops/{stop_id}",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Remove stop from trip",
)
async def remove_trip_stop(
    id: str,
    stop_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Removes a stop from a trip."""
    result = await delete_stop(db=db, stop_id=stop_id, current_user=current_user, trip_id=id)
    return APIResponse(
        success=True,
        data=result,
        message="Stop removed from trip successfully",
    )


# ============================================================================
# ITINERARY & CONFLICTS SUB-ROUTES
# ============================================================================

@router.get(
    "/{id}/itinerary",
    response_model=APIResponse[ItineraryResponseOut],
    status_code=status.HTTP_200_OK,
    summary="Get day-wise grouped itinerary",
)
async def get_day_wise_itinerary(
    id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns day-wise scheduled itinerary grouped by date then by city."""
    itinerary_data = await get_trip_itinerary(db=db, trip_id=id, current_user=current_user)
    return APIResponse(
        success=True,
        data=itinerary_data,
        message="Itinerary retrieved successfully",
    )


@router.get(
    "/{id}/conflicts",
    response_model=APIResponse[ConflictResponseOut],
    status_code=status.HTTP_200_OK,
    summary="Detect overlapping schedule conflicts",
)
async def get_schedule_conflicts(
    id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Detects overlapping activity times scheduled on the same date."""
    conflicts_data = await get_trip_conflicts(db=db, trip_id=id, current_user=current_user)
    return APIResponse(
        success=True,
        data=conflicts_data,
        message="Conflict analysis completed",
    )


@router.post(
    "/{id}/generate-itinerary",
    response_model=APIResponse[GeneratedItineraryOut],
    status_code=status.HTTP_200_OK,
    summary="AI rule-based itinerary generator",
)
async def generate_itinerary_with_ai(
    id: str,
    payload: GenerateItineraryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generates a complete day-by-day itinerary schedule based on pace and interests."""
    gen_result = await generate_ai_itinerary(db=db, trip_id=id, current_user=current_user, payload=payload)
    return APIResponse(
        success=True,
        data=gen_result,
        message="Itinerary generated successfully",
    )


# ============================================================================
# BUDGET & EXPENSES SUB-ROUTES
# ============================================================================

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
    """Computes exact 12-step budget forecast and breakdown."""
    budget_data = await calculate_trip_budget(trip_id=id, current_user=current_user, db=db)
    return APIResponse(
        success=True,
        data=budget_data,
        message="Budget calculated successfully",
    )


@router.put(
    "/{id}/budget",
    response_model=APIResponse[BudgetCalculationOut],
    status_code=status.HTTP_200_OK,
    summary="Update manual budget fields",
)
async def edit_trip_budget(
    id: str,
    payload: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates manual budget fields (transport_cost, misc_cost, limit)."""
    updated_budget = await update_trip_budget_settings(db=db, trip_id=id, current_user=current_user, payload=payload)
    return APIResponse(
        success=True,
        data=updated_budget,
        message="Budget settings updated successfully",
    )


@router.post(
    "/{id}/expenses",
    response_model=APIResponse[ExpenseOut],
    status_code=status.HTTP_201_CREATED,
    summary="Log an expense for trip",
)
async def add_expense_to_trip(
    id: str,
    payload: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Logs an expense entry under a trip."""
    expense = await create_expense(db=db, trip_id=id, current_user=current_user, payload=payload)
    return APIResponse(
        success=True,
        data=expense,
        message="Expense logged successfully",
    )


@router.get(
    "/{id}/expenses",
    response_model=APIResponse[List[ExpenseOut]],
    status_code=status.HTTP_200_OK,
    summary="List all expenses for trip",
)
async def get_all_trip_expenses(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists all estimated and actual expenses for a trip."""
    expenses = await list_trip_expenses(db=db, trip_id=id, current_user=current_user)
    return APIResponse(
        success=True,
        data=expenses,
        message="Expenses retrieved successfully",
    )


# ============================================================================
# SHARING & COLLABORATION SUB-ROUTES
# ============================================================================

@router.post(
    "/{id}/share",
    response_model=APIResponse[SharedLinkOut],
    status_code=status.HTTP_201_CREATED,
    summary="Generate public shareable link",
)
async def generate_share_link(
    id: str,
    payload: SharedLinkCreate = SharedLinkCreate(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generates a secure share token link for a trip."""
    link = await create_shared_link(db=db, trip_id=id, current_user=current_user, expires_in_days=payload.expires_in_days)
    return APIResponse(
        success=True,
        data=link,
        message="Share link generated successfully",
    )


@router.post(
    "/{id}/collaborators",
    response_model=APIResponse[CollaboratorOut],
    status_code=status.HTTP_201_CREATED,
    summary="Add collaborator to trip",
)
async def invite_collaborator(
    id: str,
    payload: CollaboratorAddRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Invites a user by email as an editor or viewer (owner only)."""
    collab = await add_collaborator(db=db, trip_id=id, current_user=current_user, payload=payload)
    return APIResponse(
        success=True,
        data=collab,
        message="Collaborator added successfully",
    )


@router.get(
    "/{id}/collaborators",
    response_model=APIResponse[List[CollaboratorOut]],
    status_code=status.HTTP_200_OK,
    summary="List trip collaborators",
)
async def get_trip_collaborators(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists collaborators for a trip."""
    collabs = await list_collaborators(db=db, trip_id=id, current_user=current_user)
    return APIResponse(
        success=True,
        data=collabs,
        message="Collaborators retrieved successfully",
    )


@router.delete(
    "/{id}/collaborators/{user_id}",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Remove a collaborator",
)
async def delete_trip_collaborator(
    id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Removes a collaborator from a trip."""
    result = await remove_collaborator(db=db, trip_id=id, user_id_to_remove=user_id, current_user=current_user)
    return APIResponse(
        success=True,
        data=result,
        message="Collaborator removed successfully",
    )


# ============================================================================
# MAP ROUTE SUB-ROUTE
# ============================================================================

@router.get(
    "/{id}/map-route",
    response_model=APIResponse[MapRouteOut],
    status_code=status.HTTP_200_OK,
    summary="Get ordered route coordinates and total distance",
)
async def get_map_route(
    id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns ordered stop coordinates and great-circle Haversine distance in km."""
    route_data = await calculate_map_route(db=db, trip_id=id, current_user=current_user)
    return APIResponse(
        success=True,
        data=route_data,
        message="Map route calculated successfully",
    )
