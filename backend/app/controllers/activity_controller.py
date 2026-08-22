from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.city import City
from app.schemas.activity import ActivityCreate


async def list_city_activities(
    db: AsyncSession,
    city_id: str,
    category: Optional[str] = None,
    activity_type: Optional[str] = None,
    max_cost: Optional[float] = None,
    max_duration: Optional[float] = None,
) -> List[Activity]:
    """
    Lists activities available in a specific city with optional category, max_cost, and max_duration filters.
    """
    city = await db.get(City, city_id)
    if city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"City with id '{city_id}' not found",
        )

    query = select(Activity).where(Activity.city_id == city_id)

    cat_filter = category or activity_type
    if cat_filter:
        query = query.where(Activity.category.ilike(f"%{cat_filter.strip()}%"))

    if max_cost is not None:
        query = query.where(Activity.estimated_cost <= max_cost)

    if max_duration is not None:
        query = query.where(Activity.duration_hours <= max_duration)

    query = query.order_by(Activity.estimated_cost.asc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_activity(db: AsyncSession, activity_id: str) -> Activity:
    """Retrieves a single activity by its ID."""
    act = await db.get(Activity, activity_id)
    if act is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with id '{activity_id}' not found",
        )
    return act


async def create_activity(db: AsyncSession, payload: ActivityCreate) -> Activity:
    """Creates a new activity catalog item in a city."""
    city = await db.get(City, payload.city_id)
    if city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"City with id '{payload.city_id}' not found",
        )

    activity = Activity(
        city_id=payload.city_id,
        name=payload.name.strip(),
        category=payload.category.strip(),
        description=payload.description,
        estimated_cost=payload.estimated_cost,
        duration_hours=payload.duration_hours,
        latitude=payload.latitude,
        longitude=payload.longitude,
        image_url=payload.image_url,
    )
    db.add(activity)
    await db.flush()
    await db.refresh(activity)
    return activity
