from datetime import date
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.activity import Activity
from app.models.budget import Budget
from app.models.city import City
from app.models.stop import Stop
from app.models.stop_activity import StopActivity
from app.models.trip import Trip
from app.models.user import User
from app.schemas.trip import TripCreate, TripUpdate


async def list_user_trips(db: AsyncSession, user_id: str) -> List[Trip]:
    """
    Lists all trips planned by the specified user.
    """
    query = (
        select(Trip)
        .where(Trip.user_id == user_id)
        .order_by(Trip.created_at.desc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_trip(db: AsyncSession, user_id: str, payload: TripCreate) -> Trip:
    """
    Creates a new trip and initializes an associated default budget record.
    """
    if payload.start_date > payload.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip start date cannot be after end date",
        )

    trip = Trip(
        user_id=user_id,
        title=payload.title.strip(),
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
        cover_photo=payload.cover_photo,
        is_public=payload.is_public,
    )
    db.add(trip)
    await db.flush()

    # Automatically create a corresponding Budget row
    budget = Budget(
        trip_id=trip.id,
        transport_cost=0.0,
        stay_cost=0.0,
        meals_cost=0.0,
        misc_cost=0.0,
        total_budget_limit=None,
    )
    db.add(budget)
    await db.flush()

    return await get_trip_detail(db=db, trip_id=trip.id, current_user=await db.get(User, user_id))


async def get_trip_detail(db: AsyncSession, trip_id: str, current_user: Optional[User] = None) -> Trip:
    """
    Retrieves full details of a trip including stops, assigned activities, and budget.
    """
    query = (
        select(Trip)
        .options(
            selectinload(Trip.budget),
            selectinload(Trip.stops)
            .selectinload(Stop.city),
            selectinload(Trip.stops)
            .selectinload(Stop.stop_activities)
            .selectinload(StopActivity.activity),
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

    # Permission check: must be owner if private
    if not trip.is_public:
        if current_user is None or trip.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this private trip",
            )

    return trip


async def update_trip(
    db: AsyncSession,
    trip_id: str,
    current_user: User,
    payload: TripUpdate,
) -> Trip:
    """
    Updates general trip information (title, dates, photo, visibility).
    """
    trip = await db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id '{trip_id}' not found",
        )

    if trip.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this trip",
        )

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
    if payload.is_public is not None:
        trip.is_public = payload.is_public

    if trip.start_date > trip.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip start date cannot be after end date",
        )

    db.add(trip)
    await db.flush()
    return await get_trip_detail(db=db, trip_id=trip.id, current_user=current_user)


async def delete_trip(db: AsyncSession, trip_id: str, current_user: User) -> dict:
    """
    Deletes a trip and cascades all attached stops and budget entries.
    """
    trip = await db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id '{trip_id}' not found",
        )

    if trip.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this trip",
        )

    await db.delete(trip)
    await db.flush()
    return {"message": "Trip deleted successfully"}


async def get_public_trip(db: AsyncSession, trip_id: str) -> Trip:
    """
    Retrieves public read-only view of a trip without requiring authentication.
    """
    query = (
        select(Trip)
        .options(
            selectinload(Trip.stops).selectinload(Stop.city),
            selectinload(Trip.stops)
            .selectinload(Stop.stop_activities)
            .selectinload(StopActivity.activity),
        )
        .where(Trip.id == trip_id, Trip.is_public.is_(True))
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
    Upgraded multi-step trip budget calculation engine:
    - Validates ownership for current_user
    - STEP 1: Fetch base data (trip, stops, activities, budgets row)
    - STEP 2: Calculate stay_cost across all stops (minimum 1 day per stop, default city cost 80.0)
    - STEP 3: Calculate activities_cost (sum of stop activities, default 0.0)
    - STEP 4: Calculate meals_cost (MEALS_PER_DAY_USD * total_trip_days)
    - STEP 5: Load transport_cost and misc_cost from budget table
    - STEP 6: Compute total_cost
    - STEP 7: Compute cost_per_day
    - STEP 8: Calculate savings_needed_per_day and determine trip_status
    - STEP 9: Compute budget overage and remaining balance
    - STEP 10: Generate per-stop breakdown
    - STEP 11: Calculate cost distribution percentages
    """
    # -------------------------------------------------------------
    # STEP 1 — Fetch base data & Validate ownership
    # -------------------------------------------------------------
    query = (
        select(Trip)
        .options(
            selectinload(Trip.budget),
            selectinload(Trip.stops).selectinload(Stop.city),
            selectinload(Trip.stops)
            .selectinload(Stop.stop_activities)
            .selectinload(StopActivity.activity),
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

    if trip.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this trip's budget",
        )

    # Edge Case 4: total_trip_days minimum = 1 (never divide by zero)
    days_diff = (trip.end_date - trip.start_date).days
    total_trip_days = max(1, days_diff if days_diff > 0 else 1)

    # Edge Case 3: Ensure budget record exists
    if trip.budget is None:
        trip.budget = Budget(
            trip_id=trip.id,
            transport_cost=0.0,
            stay_cost=0.0,
            meals_cost=0.0,
            misc_cost=0.0,
            total_budget_limit=None,
        )
        db.add(trip.budget)
        await db.flush()

    # -------------------------------------------------------------
    # STEP 2 & 10 — stay_cost & per-stop breakdown
    # -------------------------------------------------------------
    stop_breakdown = []
    has_stops = len(trip.stops) > 0

    if has_stops:
        for stop in trip.stops:
            # Edge Case 2: arrival_date == departure_date -> days_at_stop = 1
            stop_days_diff = (stop.departure_date - stop.arrival_date).days
            days_at_stop = max(1, stop_days_diff if stop_days_diff > 0 else 1)

            # Edge Case 7: city.cost_index is NULL -> default 80.0 USD
            city_cost_index = 80.0
            city_name = "Unknown City"
            if stop.city:
                city_name = stop.city.name
                if stop.city.cost_index is not None:
                    city_cost_index = float(stop.city.cost_index)

            stop_stay_cost = round(city_cost_index * days_at_stop, 2)

            # Edge Case 6: Activity cost is NULL -> treat as 0.0
            stop_activities_cost = 0.0
            for sa in stop.stop_activities:
                if sa.activity and sa.activity.cost is not None:
                    stop_activities_cost += float(sa.activity.cost)
            stop_activities_cost = round(stop_activities_cost, 2)

            stop_meals_cost = round(settings.MEALS_PER_DAY_USD * days_at_stop, 2)
            stop_total = round(stop_stay_cost + stop_activities_cost + stop_meals_cost, 2)

            stop_breakdown.append({
                "stop_id": stop.id,
                "city_name": city_name,
                "days": days_at_stop,
                "stay_cost": stop_stay_cost,
                "activities_cost": stop_activities_cost,
                "meals_cost": stop_meals_cost,
                "stop_total": stop_total,
            })

        stay_cost = round(sum(s["stay_cost"] for s in stop_breakdown), 2)
        activities_cost = round(sum(s["activities_cost"] for s in stop_breakdown), 2)
        # STEP 4: meals_cost based on total_trip_days
        meals_cost = round(settings.MEALS_PER_DAY_USD * total_trip_days, 2)
    else:
        # Edge Case 1: Trip has NO stops yet
        stay_cost = 0.0
        activities_cost = 0.0
        meals_cost = 0.0

    # -------------------------------------------------------------
    # STEP 5 — transport_cost and misc_cost
    # -------------------------------------------------------------
    transport_cost = round(float(trip.budget.transport_cost or 0.0), 2)
    misc_cost = round(float(trip.budget.misc_cost or 0.0), 2)

    # -------------------------------------------------------------
    # STEP 6 — total_cost
    # -------------------------------------------------------------
    total_cost = round(stay_cost + activities_cost + meals_cost + transport_cost + misc_cost, 2)

    # -------------------------------------------------------------
    # STEP 7 — cost_per_day
    # -------------------------------------------------------------
    cost_per_day = round(total_cost / total_trip_days, 2)

    # -------------------------------------------------------------
    # STEP 8 — savings_needed_per_day & trip_status
    # -------------------------------------------------------------
    today_date = date.today()
    days_until_trip = (trip.start_date - today_date).days

    if today_date > trip.end_date:
        trip_status = "completed"
    elif today_date >= trip.start_date:
        trip_status = "ongoing"
    else:
        trip_status = "upcoming"

    # Edge Case 5: trip already started (start_date <= today)
    if days_until_trip > 0:
        savings_needed_per_day = round(total_cost / days_until_trip, 2)
    else:
        savings_needed_per_day = None

    # -------------------------------------------------------------
    # STEP 9 — is_over_budget + overage
    # -------------------------------------------------------------
    total_budget_limit = trip.budget.total_budget_limit
    if total_budget_limit is not None:
        total_budget_limit = round(float(total_budget_limit), 2)
        is_over_budget = total_cost > total_budget_limit
        budget_overage = round(total_cost - total_budget_limit, 2)
        budget_remaining = round(total_budget_limit - total_cost, 2)
    else:
        is_over_budget = None
        budget_overage = None
        budget_remaining = None

    # -------------------------------------------------------------
    # STEP 11 — cost_distribution_percent
    # -------------------------------------------------------------
    if total_cost > 0:
        cost_dist_percent = {
            "stay": round((stay_cost / total_cost) * 100, 1),
            "activities": round((activities_cost / total_cost) * 100, 1),
            "meals": round((meals_cost / total_cost) * 100, 1),
            "transport": round((transport_cost / total_cost) * 100, 1),
            "misc": round((misc_cost / total_cost) * 100, 1),
        }
    else:
        cost_dist_percent = {
            "stay": 0.0,
            "activities": 0.0,
            "meals": 0.0,
            "transport": 0.0,
            "misc": 0.0,
        }

    # Synchronize database budget row with calculated figures
    trip.budget.stay_cost = stay_cost
    trip.budget.meals_cost = meals_cost
    db.add(trip.budget)
    await db.flush()

    return {
        "trip_id": trip.id,
        "trip_title": trip.title,
        "trip_status": trip_status,
        "total_trip_days": total_trip_days,
        "days_until_trip": days_until_trip if days_until_trip >= 0 else None,
        "cost_breakdown": {
            "stay_cost": stay_cost,
            "activities_cost": activities_cost,
            "meals_cost": meals_cost,
            "transport_cost": transport_cost,
            "misc_cost": misc_cost,
            "total_cost": total_cost,
        },
        "per_day": {
            "cost_per_day": cost_per_day,
            "savings_needed_per_day": savings_needed_per_day,
        },
        "budget_status": {
            "total_budget_limit": total_budget_limit,
            "is_over_budget": is_over_budget,
            "budget_overage": budget_overage,
            "budget_remaining": budget_remaining,
        },
        "stop_breakdown": stop_breakdown,
        "cost_distribution_percent": cost_dist_percent,
    }
