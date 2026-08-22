from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.city import City
from app.models.stop import Stop
from app.models.stop_activity import StopActivity
from app.models.trip import Trip
from app.models.user import User
from app.schemas.stop import StopCreate, StopUpdate


async def add_stop(
    db: AsyncSession,
    trip_id: str,
    current_user: User,
    payload: StopCreate,
) -> Stop:
    """
    Adds a new destination stop to an existing trip.
    """
    # Verify trip exists and belongs to user
    trip = await db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id '{trip_id}' not found",
        )

    if trip.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to add stops to this trip",
        )

    # Verify city exists
    city = await db.get(City, payload.city_id)
    if city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"City with id '{payload.city_id}' not found",
        )

    if payload.arrival_date > payload.departure_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stop arrival date cannot be after departure date",
        )

    stop = Stop(
        trip_id=trip_id,
        city_id=payload.city_id,
        arrival_date=payload.arrival_date,
        departure_date=payload.departure_date,
        order_index=payload.order_index,
    )
    db.add(stop)
    await db.flush()

    # Query with relationships loaded
    result = await db.execute(
        select(Stop)
        .options(
            selectinload(Stop.city),
            selectinload(Stop.stop_activities).selectinload(StopActivity.activity),
        )
        .where(Stop.id == stop.id)
    )
    return result.scalar_one()


async def update_stop(
    db: AsyncSession,
    stop_id: str,
    current_user: User,
    payload: StopUpdate,
) -> Stop:
    """
    Updates stop dates or order index.
    """
    result = await db.execute(
        select(Stop)
        .options(
            selectinload(Stop.trip),
            selectinload(Stop.city),
            selectinload(Stop.stop_activities).selectinload(StopActivity.activity),
        )
        .where(Stop.id == stop_id)
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
            detail="You do not have permission to update this stop",
        )

    if payload.arrival_date is not None:
        stop.arrival_date = payload.arrival_date
    if payload.departure_date is not None:
        stop.departure_date = payload.departure_date
    if payload.order_index is not None:
        stop.order_index = payload.order_index

    if stop.arrival_date > stop.departure_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stop arrival date cannot be after departure date",
        )

    db.add(stop)
    await db.flush()
    await db.refresh(stop)
    return stop


async def delete_stop(
    db: AsyncSession,
    stop_id: str,
    current_user: User,
) -> dict:
    """
    Deletes a stop and its assigned activities from a trip.
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
            detail="You do not have permission to delete this stop",
        )

    await db.delete(stop)
    await db.flush()
    return {"message": "Stop removed from trip successfully"}
