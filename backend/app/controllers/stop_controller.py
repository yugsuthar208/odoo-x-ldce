from typing import List
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.controllers.trip_controller import get_trip_and_check_access
from app.models.city import City
from app.models.itinerary_item import ItineraryItem
from app.models.stop import TripStop
from app.models.user import User
from app.schemas.stop import StopCreate, StopReorderItem, StopUpdate


async def add_stop(
    db: AsyncSession,
    trip_id: str,
    current_user: User,
    payload: StopCreate,
) -> TripStop:
    """Adds a stop to a trip checking editor/owner permission and date bounds."""
    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="editor")

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

    if payload.arrival_date < trip.start_date or payload.departure_date > trip.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stop dates ({payload.arrival_date} to {payload.departure_date}) must be within trip dates ({trip.start_date} to {trip.end_date})",
        )

    stop_order = payload.stop_order if payload.order_index is None else payload.order_index

    stop = TripStop(
        trip_id=trip_id,
        city_id=payload.city_id,
        arrival_date=payload.arrival_date,
        departure_date=payload.departure_date,
        stop_order=stop_order,
        notes=payload.notes,
    )
    db.add(stop)
    await db.flush()

    res_trip = await db.execute(
        select(Trip)
        .options(
            selectinload(Trip.stops).selectinload(TripStop.city),
            selectinload(Trip.transit_legs),
        )
        .where(Trip.id == trip_id)
    )
    trip = res_trip.scalar_one()

    from app.services.transit_service import TransitService
    await TransitService.rebuild_transit_legs(db, trip)

    result = await db.execute(
        select(TripStop)
        .options(
            selectinload(TripStop.city),
            selectinload(TripStop.itinerary_items).selectinload(ItineraryItem.activity),
        )
        .where(TripStop.id == stop.id)
    )
    return result.scalar_one()


async def update_stop(
    db: AsyncSession,
    stop_id: str,
    current_user: User,
    payload: StopUpdate,
    trip_id: str = None,
) -> TripStop:
    """Updates stop dates, order, or notes with date range checks."""
    result = await db.execute(
        select(TripStop)
        .options(
            selectinload(TripStop.trip),
            selectinload(TripStop.city),
            selectinload(TripStop.itinerary_items).selectinload(ItineraryItem.activity),
        )
        .where(TripStop.id == stop_id)
    )
    stop = result.scalar_one_or_none()

    if stop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stop with id '{stop_id}' not found",
        )

    if trip_id and stop.trip_id != trip_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stop does not belong to specified trip",
        )

    trip = await get_trip_and_check_access(db=db, trip_id=stop.trip_id, user_id=current_user.id, required_role="editor")

    new_arr = payload.arrival_date if payload.arrival_date is not None else stop.arrival_date
    new_dep = payload.departure_date if payload.departure_date is not None else stop.departure_date

    if new_arr > new_dep:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stop arrival date cannot be after departure date",
        )

    if new_arr < trip.start_date or new_dep > trip.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stop dates ({new_arr} to {new_dep}) must be within trip dates ({trip.start_date} to {trip.end_date})",
        )

    stop.arrival_date = new_arr
    stop.departure_date = new_dep
    if payload.stop_order is not None:
        stop.stop_order = payload.stop_order
    elif payload.order_index is not None:
        stop.stop_order = payload.order_index
    if payload.notes is not None:
        stop.notes = payload.notes

    db.add(stop)
    await db.flush()
    await db.refresh(stop)
    return stop


async def delete_stop(
    db: AsyncSession,
    stop_id: str,
    current_user: User,
    trip_id: str = None,
) -> dict:
    """Deletes a stop from a trip."""
    result = await db.execute(select(TripStop).where(TripStop.id == stop_id))
    stop = result.scalar_one_or_none()

    if stop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stop with id '{stop_id}' not found",
        )

    if trip_id and stop.trip_id != trip_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stop does not belong to specified trip",
        )

    trip = await get_trip_and_check_access(db=db, trip_id=stop.trip_id, user_id=current_user.id, required_role="editor")

    await db.delete(stop)
    await db.flush()
    await db.refresh(trip, ["stops", "transit_legs"])
    
    from app.services.transit_service import TransitService
    await TransitService.rebuild_transit_legs(db, trip)
    
    return {"message": "Stop removed from trip successfully"}


async def reorder_stops(
    db: AsyncSession,
    trip_id: str,
    current_user: User,
    items: List[StopReorderItem],
) -> List[TripStop]:
    """
    Bulk updates order for all stops in a trip and rebuilds transit legs in a single transaction.
    Validates that:
      1. All stop IDs belong to the trip.
      2. Provided stop IDs are unique.
    """
    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="editor")

    provided_stop_ids = [item.stop_id for item in items]
    if len(provided_stop_ids) != len(set(provided_stop_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate stop IDs provided in reorder payload",
        )

    existing_stops_res = await db.execute(select(TripStop).where(TripStop.trip_id == trip_id))
    existing_stops = {s.id: s for s in existing_stops_res.scalars().all()}

    for sid in provided_stop_ids:
        if sid not in existing_stops:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stop '{sid}' does not belong to trip '{trip_id}'",
            )

    for item in items:
        stop = existing_stops[item.stop_id]
        stop.stop_order = item.get_order()
        db.add(stop)

    await db.flush()

    res_trip = await db.execute(
        select(Trip)
        .options(
            selectinload(Trip.stops).selectinload(TripStop.city),
            selectinload(Trip.transit_legs),
        )
        .where(Trip.id == trip_id)
    )
    trip = res_trip.scalar_one()
    
    from app.services.transit_service import TransitService
    await TransitService.rebuild_transit_legs(db, trip)

    result = await db.execute(
        select(TripStop)
        .options(
            selectinload(TripStop.city),
            selectinload(TripStop.itinerary_items).selectinload(ItineraryItem.activity),
        )
        .where(TripStop.trip_id == trip_id)
        .order_by(TripStop.stop_order.asc())
    )
    return list(result.scalars().all())

