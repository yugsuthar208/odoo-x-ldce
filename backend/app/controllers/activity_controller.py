from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity import Activity
from app.models.city import City
from app.models.stop import Stop
from app.models.stop_activity import StopActivity
from app.models.trip import Trip
from app.models.user import User
from app.schemas.activity import ActivityCreate, StopActivityAssign


async def list_city_activities(
    db: AsyncSession,
    city_id: str,
    activity_type: Optional[str] = None,
    max_cost: Optional[float] = None,
) -> List[Activity]:
    """
    Lists activities available in a specific city with optional type and max_cost filters.
    """
    # Verify city exists
    city = await db.get(City, city_id)
    if city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"City with id '{city_id}' not found",
        )

    query = select(Activity).where(Activity.city_id == city_id)

    if activity_type:
        query = query.where(Activity.type.ilike(activity_type.strip()))

    if max_cost is not None:
        query = query.where(Activity.cost <= max_cost)

    query = query.order_by(Activity.cost.asc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_activity(db: AsyncSession, payload: ActivityCreate) -> Activity:
    """Creates a new activity in a city."""
    city = await db.get(City, payload.city_id)
    if city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"City with id '{payload.city_id}' not found",
        )

    activity = Activity(
        city_id=payload.city_id,
        name=payload.name.strip(),
        type=payload.type.strip(),
        description=payload.description,
        cost=payload.cost,
        duration_hours=payload.duration_hours,
        image_url=payload.image_url,
    )
    db.add(activity)
    await db.flush()
    await db.refresh(activity)
    return activity


async def assign_activity_to_stop(
    db: AsyncSession,
    stop_id: str,
    current_user: User,
    payload: StopActivityAssign,
) -> StopActivity:
    """
    Assigns an activity to a stop after verifying ownership.
    """
    # Fetch stop along with its parent trip
    result = await db.execute(
        select(Stop).options(selectinload(Stop.trip)).where(Stop.id == stop_id)
    )
    stop = result.scalar_one_or_none()

    if stop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stop with id '{stop_id}' not found",
        )

    if stop.trip.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this trip's stops",
        )

    # Verify activity exists
    activity = await db.get(Activity, payload.activity_id)
    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with id '{payload.activity_id}' not found",
        )

    stop_activity = StopActivity(
        stop_id=stop_id,
        activity_id=payload.activity_id,
        scheduled_date=payload.scheduled_date,
        scheduled_time=payload.scheduled_time,
        notes=payload.notes,
    )
    db.add(stop_activity)
    await db.flush()

    # Load with relationship
    result_sa = await db.execute(
        select(StopActivity)
        .options(selectinload(StopActivity.activity))
        .where(StopActivity.id == stop_activity.id)
    )
    return result_sa.scalar_one()


async def remove_activity_from_stop(
    db: AsyncSession,
    stop_id: str,
    activity_id: str,
    current_user: User,
) -> dict:
    """
    Removes an activity assignment from a stop.
    """
    result = await db.execute(
        select(Stop).options(selectinload(Stop.trip)).where(Stop.id == stop_id)
    )
    stop = result.scalar_one_or_none()

    if stop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stop with id '{stop_id}' not found",
        )

    if stop.trip.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this trip's activities",
        )

    # Find the StopActivity record by stop_id and activity_id (or stop_activity id)
    sa_result = await db.execute(
        select(StopActivity).where(
            StopActivity.stop_id == stop_id,
            (StopActivity.activity_id == activity_id) | (StopActivity.id == activity_id),
        )
    )
    stop_activity = sa_result.scalar_one_or_none()

    if stop_activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity assignment not found on this stop",
        )

    await db.delete(stop_activity)
    await db.flush()
    return {"message": "Activity removed from stop successfully"}
