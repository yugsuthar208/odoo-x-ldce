import math
from datetime import date, datetime
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.activity import Activity
from app.models.budget import Budget
from app.models.city import City
from app.models.expense import Expense
from app.models.itinerary_item import ItineraryItem
from app.models.shared_link import SharedLink
from app.models.stop import TripStop
from app.models.trip import Trip
from app.models.trip_collaborator import TripCollaborator
from app.models.user import User
from app.models.transit import TransitLeg
from app.models.stay import TripStay
from app.schemas.trip import TripCreate, TripUpdate
from app.services.audit_service import log_audit_event
from app.services.websocket_manager import ws_manager


async def get_trip_and_check_access(
    db: AsyncSession,
    trip_id: str,
    user_id: Optional[str] = None,
    required_role: str = "viewer",  # "viewer" or "editor" or "owner"
) -> Trip:
    """
    Fetches a trip and verifies access permissions:
    - Owner has full permissions (owner, editor, viewer).
    - Collaborator with role="editor" has editor & viewer permissions.
    - Collaborator with role="viewer" has viewer permission.
    - Public trip (visibility="public") is accessible for viewer without authentication.
    """
    query = (
        select(Trip)
        .options(
            selectinload(Trip.budget),
            selectinload(Trip.stops).selectinload(TripStop.city),
            selectinload(Trip.stops).selectinload(TripStop.itinerary_items).selectinload(ItineraryItem.activity),
            selectinload(Trip.stops).selectinload(TripStop.stay_info),
            selectinload(Trip.transit_legs).selectinload(TransitLeg.options),
            selectinload(Trip.transit_legs).selectinload(TransitLeg.selected_option),
            selectinload(Trip.collaborators).selectinload(TripCollaborator.user),
            selectinload(Trip.expenses),
        )
        .where(Trip.id == trip_id)
    )
    result = await db.execute(query)
    trip = result.scalar_one_or_none()

    if trip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id '{trip_id}' not found",
        )

    # If public and only viewer access needed, allow
    if trip.visibility == "public" and required_role == "viewer":
        return trip

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to access this trip",
        )

    # Owner has all access
    if trip.user_id == user_id:
        return trip

    # Check collaborators
    collaborator_roles = {c.user_id: c.role for c in trip.collaborators}
    user_role = collaborator_roles.get(user_id)

    if required_role == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the trip owner can perform this action",
        )
    elif required_role == "editor":
        if user_role != "editor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be an editor or owner to modify this trip",
            )
    elif required_role == "viewer":
        if user_role not in ["editor", "viewer"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this trip",
            )

    return trip


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the great-circle distance between two points in kilometers."""
    R = 6371.0  # Earth radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


async def list_user_trips(
    db: AsyncSession,
    user_id: str,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Trip]:
    """
    Lists trips where user is owner or collaborator with optional status and search filtering.
    """
    collab_subq = select(TripCollaborator.trip_id).where(TripCollaborator.user_id == user_id)
    query = (
        select(Trip)
        .where(or_(Trip.user_id == user_id, Trip.id.in_(collab_subq)))
        .order_by(Trip.created_at.desc())
    )

    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(or_(Trip.title.ilike(pattern), Trip.description.ilike(pattern)))

    result = await db.execute(query)
    trips = list(result.scalars().all())

    # Update dynamic status if needed and apply status filter
    filtered_trips = []
    for trip in trips:
        calc_status = trip.dynamic_status()
        if trip.status != "draft" and trip.status != calc_status:
            trip.status = calc_status
            db.add(trip)
        if status_filter:
            if trip.status.lower() == status_filter.lower():
                filtered_trips.append(trip)
        else:
            filtered_trips.append(trip)

    return filtered_trips


async def create_trip(db: AsyncSession, user_id: str, payload: TripCreate) -> Trip:
    """Creates a new trip and its budget."""
    if payload.start_date > payload.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip start date cannot be after end date",
        )

    visibility = payload.visibility or ("public" if payload.is_public else "private")
    status_val = payload.status or "draft"

    trip = Trip(
        user_id=user_id,
        title=payload.title.strip(),
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
        cover_photo=payload.cover_photo,
        origin_city=payload.origin_city or "Mumbai",
        num_travelers=payload.num_travelers or 1,
        transit_mode=payload.transit_mode or "train",
        total_budget=payload.total_budget,
        currency=payload.currency or "INR",
        visibility=visibility,
        status=status_val,
    )
    db.add(trip)
    await db.flush()

    budget = Budget(
        trip_id=trip.id,
        transport_cost=0.0,
        stay_cost=0.0,
        meals_cost=0.0,
        misc_cost=0.0,
        total_budget_limit=payload.total_budget,
    )
    db.add(budget)
    await db.flush()

    # Log audit event
    await log_audit_event(
        db=db,
        action="TRIP_CREATED",
        resource_type="trip",
        resource_id=trip.id,
        user_id=user_id,
        trip_id=trip.id,
        details={"title": trip.title, "total_budget": trip.total_budget},
    )

    return await get_trip_detail(db=db, trip_id=trip.id, current_user=await db.get(User, user_id))


async def get_trip_detail(db: AsyncSession, trip_id: str, current_user: Optional[User] = None) -> Trip:
    """Retrieves full trip details checking viewer permission."""
    user_id = current_user.id if current_user else None
    return await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=user_id, required_role="viewer")


async def update_trip(
    db: AsyncSession,
    trip_id: str,
    current_user: User,
    payload: TripUpdate,
) -> Trip:
    """Updates trip details checking editor/owner permission."""
    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="editor")

    if payload.title is not None:
        trip.title = payload.title.strip()
    if payload.description is not None:
        trip.description = payload.description
    if payload.start_date is not None:
        trip.start_date = payload.start_date
    if payload.end_date is not None:
        trip.end_date = payload.end_date
    if payload.cover_photo is not None:
        trip.cover_photo = payload.cover_photo
    if payload.origin_city is not None:
        trip.origin_city = payload.origin_city
    if payload.num_travelers is not None:
        trip.num_travelers = payload.num_travelers
    if payload.transit_mode is not None:
        trip.transit_mode = payload.transit_mode
    if payload.total_budget is not None:
        trip.total_budget = payload.total_budget
        if trip.budget:
            trip.budget.total_budget_limit = payload.total_budget
    if payload.currency is not None:
        trip.currency = payload.currency
    if payload.visibility is not None:
        trip.visibility = payload.visibility
    elif payload.is_public is not None:
        trip.visibility = "public" if payload.is_public else "private"
    if payload.status is not None:
        if not trip.can_transition_to(payload.status):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Illegal trip status transition from '{trip.status}' to '{payload.status}'. Use lifecycle endpoints.",
            )
        trip.status = payload.status

    if trip.start_date > trip.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip start date cannot be after end date",
        )

    db.add(trip)
    await db.flush()

    # Log audit event
    await log_audit_event(
        db=db,
        action="TRIP_UPDATED",
        resource_type="trip",
        resource_id=trip.id,
        user_id=current_user.id,
        trip_id=trip.id,
        details=payload.model_dump(exclude_unset=True, mode="json"),
    )

    # Broadcast real-time update to WebSocket room
    await ws_manager.broadcast_to_trip(
        trip_id=trip.id,
        message={
            "type": "TRIP_MODIFIED",
            "action": "TRIP_UPDATED",
            "user": {"id": current_user.id, "full_name": current_user.full_name},
            "trip_id": trip.id,
        }
    )

    return await get_trip_detail(db=db, trip_id=trip.id, current_user=current_user)


async def delete_trip(db: AsyncSession, trip_id: str, current_user: User) -> dict:
    """Deletes trip (owner only) cascading all related entities."""
    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="owner")
    
    # Log audit event before deletion
    await log_audit_event(
        db=db,
        action="TRIP_DELETED",
        resource_type="trip",
        resource_id=trip.id,
        user_id=current_user.id,
        trip_id=trip.id,
        details={"title": trip.title},
    )

    await db.delete(trip)
    await db.flush()

    # Broadcast trip deletion
    await ws_manager.broadcast_to_trip(
        trip_id=trip_id,
        message={
            "type": "TRIP_MODIFIED",
            "action": "TRIP_DELETED",
            "user": {"id": current_user.id, "full_name": current_user.full_name},
            "trip_id": trip_id,
        }
    )

    return {"message": "Trip deleted successfully"}


async def duplicate_trip(db: AsyncSession, trip_id: str, current_user: User) -> Trip:
    """
    Copies entire trip including stops, assigned itinerary items, and budget configuration as a new draft.
    """
    stmt = (
        select(Trip)
        .options(
            selectinload(Trip.stops).selectinload(TripStop.itinerary_items),
            selectinload(Trip.budget),
            selectinload(Trip.shared_links),
        )
        .where(Trip.id == trip_id)
    )
    res = await db.execute(stmt)
    source_trip = res.scalar_one_or_none()
    if not source_trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    if source_trip.user_id != current_user.id and source_trip.visibility != "public" and len(source_trip.shared_links) == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to copy this trip")

    new_trip = Trip(
        user_id=current_user.id,
        title=f"Copy of {source_trip.title}",
        description=source_trip.description,
        start_date=source_trip.start_date,
        end_date=source_trip.end_date,
        cover_photo=source_trip.cover_photo,
        total_budget=source_trip.total_budget,
        currency=source_trip.currency,
        visibility="private",
        status="draft",
    )
    db.add(new_trip)
    await db.flush()

    new_budget = Budget(
        trip_id=new_trip.id,
        transport_cost=source_trip.budget.transport_cost if source_trip.budget else 0.0,
        stay_cost=source_trip.budget.stay_cost if source_trip.budget else 0.0,
        meals_cost=source_trip.budget.meals_cost if source_trip.budget else 0.0,
        misc_cost=source_trip.budget.misc_cost if source_trip.budget else 0.0,
        total_budget_limit=source_trip.budget.total_budget_limit if source_trip.budget else None,
    )
    db.add(new_budget)
    await db.flush()

    for stop in source_trip.stops:
        new_stop = TripStop(
            trip_id=new_trip.id,
            city_id=stop.city_id,
            arrival_date=stop.arrival_date,
            departure_date=stop.departure_date,
            stop_order=stop.stop_order,
            notes=stop.notes,
        )
        db.add(new_stop)
        await db.flush()

        for item in stop.itinerary_items:
            new_item = ItineraryItem(
                trip_stop_id=new_stop.id,
                activity_id=item.activity_id,
                scheduled_date=item.scheduled_date,
                start_time=item.start_time,
                end_time=item.end_time,
                custom_cost=item.custom_cost,
                notes=item.notes,
                status="planned",
            )
            db.add(new_item)

    await db.flush()
    return await get_trip_detail(db=db, trip_id=new_trip.id, current_user=current_user)


async def get_public_trip(db: AsyncSession, trip_id: str) -> Trip:
    """Retrieves public read-only view of a trip."""
    query = (
        select(Trip)
        .options(
            selectinload(Trip.stops).selectinload(TripStop.city),
            selectinload(Trip.stops).selectinload(TripStop.itinerary_items).selectinload(ItineraryItem.activity),
        )
        .where(Trip.id == trip_id, Trip.visibility == "public")
    )
    result = await db.execute(query)
    trip = result.scalar_one_or_none()

    if trip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public trip not found or trip is set to private",
        )
    return trip


async def calculate_trip_budget(
    trip_id: str,
    current_user: User,
    db: AsyncSession,
) -> dict:
    """
    Computes budget by delegating to the authoritative BudgetService.
    """
    await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="viewer")
    from app.services.budget_service import BudgetService
    return await BudgetService.calculate_authoritative_budget(db, trip_id)


async def calculate_map_route(
    db: AsyncSession,
    trip_id: str,
    current_user: Optional[User] = None,
) -> dict:
    """
    Computes ordered route coordinates and total distance using the Haversine formula.
    """
    user_id = current_user.id if current_user else None
    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=user_id, required_role="viewer")

    ordered_stops = sorted(trip.stops, key=lambda s: s.stop_order)
    route_points = []
    total_distance = 0.0

    prev_lat, prev_lon = None, None
    for s in ordered_stops:
        city = s.city
        lat = city.latitude if (city and city.latitude is not None) else 0.0
        lon = city.longitude if (city and city.longitude is not None) else 0.0
        days_diff = (s.departure_date - s.arrival_date).days
        days = max(1, days_diff if days_diff > 0 else 1)

        route_points.append({
            "stop_order": s.stop_order,
            "city_name": city.name if city else "Unknown",
            "country": city.country if city else "Unknown",
            "latitude": lat,
            "longitude": lon,
            "arrival_date": s.arrival_date,
            "departure_date": s.departure_date,
            "days": days,
        })

        if prev_lat is not None and prev_lon is not None:
            total_distance += haversine_distance(prev_lat, prev_lon, lat, lon)
        prev_lat, prev_lon = lat, lon

    return {
        "trip_id": trip.id,
        "route": route_points,
        "total_cities": len(route_points),
        "total_distance_km": round(total_distance, 2),
    }
