from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.controllers.trip_controller import get_trip_and_check_access
from app.models.activity import Activity
from app.models.itinerary_item import ItineraryItem
from app.models.stop import TripStop
from app.models.user import User
from app.schemas.itinerary_item import (
    ConflictDetailOut,
    ConflictItemInfo,
    ConflictResponseOut,
    DayItineraryStopGroup,
    ItineraryDayOut,
    ItineraryItemCreate,
    ItineraryItemOut,
    ItineraryItemUpdate,
    ItineraryResponseOut,
)


async def add_itinerary_item(
    db: AsyncSession,
    stop_id: str,
    current_user: User,
    payload: ItineraryItemCreate,
) -> ItineraryItem:
    """Assigns an activity to a stop checking editor/owner permissions."""
    result = await db.execute(
        select(TripStop).options(selectinload(TripStop.trip)).where(TripStop.id == stop_id)
    )
    stop = result.scalar_one_or_none()

    if stop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stop with id '{stop_id}' not found",
        )

    await get_trip_and_check_access(db=db, trip_id=stop.trip_id, user_id=current_user.id, required_role="editor")

    activity = await db.get(Activity, payload.activity_id)
    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with id '{payload.activity_id}' not found",
        )

    item = ItineraryItem(
        trip_stop_id=stop_id,
        activity_id=payload.activity_id,
        scheduled_date=payload.scheduled_date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        custom_cost=payload.custom_cost,
        notes=payload.notes,
        status=payload.status or "planned",
    )
    db.add(item)
    await db.flush()

    res = await db.execute(
        select(ItineraryItem)
        .options(selectinload(ItineraryItem.activity))
        .where(ItineraryItem.id == item.id)
    )
    return res.scalar_one()


async def update_itinerary_item(
    db: AsyncSession,
    item_id: str,
    current_user: User,
    payload: ItineraryItemUpdate,
) -> ItineraryItem:
    """Updates an itinerary item."""
    result = await db.execute(
        select(ItineraryItem)
        .options(
            selectinload(ItineraryItem.trip_stop).selectinload(TripStop.trip),
            selectinload(ItineraryItem.activity),
        )
        .where(ItineraryItem.id == item_id)
    )
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Itinerary item with id '{item_id}' not found",
        )

    await get_trip_and_check_access(db=db, trip_id=item.trip_stop.trip_id, user_id=current_user.id, required_role="editor")

    if payload.scheduled_date is not None:
        item.scheduled_date = payload.scheduled_date
    if payload.start_time is not None:
        item.start_time = payload.start_time
    if payload.end_time is not None:
        item.end_time = payload.end_time
    if payload.custom_cost is not None:
        item.custom_cost = payload.custom_cost
    if payload.notes is not None:
        item.notes = payload.notes
    if payload.status is not None:
        item.status = payload.status

    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


async def delete_itinerary_item(
    db: AsyncSession,
    item_id: str,
    current_user: User,
) -> dict:
    """Deletes an itinerary item."""
    result = await db.execute(
        select(ItineraryItem)
        .options(selectinload(ItineraryItem.trip_stop))
        .where(ItineraryItem.id == item_id)
    )
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Itinerary item with id '{item_id}' not found",
        )

    await get_trip_and_check_access(db=db, trip_id=item.trip_stop.trip_id, user_id=current_user.id, required_role="editor")

    await db.delete(item)
    await db.flush()
    return {"message": "Itinerary item deleted successfully"}


async def get_trip_itinerary(
    db: AsyncSession,
    trip_id: str,
    current_user: Optional[User] = None,
) -> dict:
    """
    Returns full day-wise itinerary grouped by date then by stop/city.
    """
    user_id = current_user.id if current_user else None
    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=user_id, required_role="viewer")

    # Map items by date -> stop_id -> list of items
    date_stop_map = defaultdict(lambda: defaultdict(list))
    total_cost = 0.0
    total_items = 0

    for stop in trip.stops:
        for item in stop.itinerary_items:
            total_items += 1
            cost = item.effective_cost
            total_cost += cost
            date_key = item.scheduled_date.isoformat() if item.scheduled_date else "Unscheduled"
            date_stop_map[date_key][stop].append(item)

    days_out = []
    # Sort dates chronologically with Unscheduled at the end
    sorted_date_keys = sorted([k for k in date_stop_map.keys() if k != "Unscheduled"])
    if "Unscheduled" in date_stop_map:
        sorted_date_keys.append("Unscheduled")

    for d_key in sorted_date_keys:
        stop_groups = []
        day_cost = 0.0
        day_count = 0
        for stop, items in date_stop_map[d_key].items():
            # sort items by start_time
            sorted_items = sorted(items, key=lambda x: str(x.start_time or "99:99"))
            items_out = [ItineraryItemOut.model_validate(it) for it in sorted_items]
            for it in items:
                day_cost += it.effective_cost
                day_count += 1
            stop_groups.append(
                DayItineraryStopGroup(
                    stop_id=stop.id,
                    city_name=stop.city.name if stop.city else "Unknown City",
                    activities=items_out,
                )
            )

        days_out.append(
            ItineraryDayOut(
                date=d_key,
                stops=stop_groups,
                day_total_cost=round(day_cost, 2),
                day_total_items=day_count,
            )
        )

    return {
        "trip_id": trip.id,
        "trip_title": trip.title,
        "days": days_out,
        "total_items": total_items,
        "total_estimated_cost": round(total_cost, 2),
    }


async def get_trip_conflicts(
    db: AsyncSession,
    trip_id: str,
    current_user: Optional[User] = None,
) -> dict:
    """
    Detects overlapping scheduled activity times on the same date:
    item_a.start_time < item_b.end_time AND item_a.end_time > item_b.start_time
    """
    user_id = current_user.id if current_user else None
    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=user_id, required_role="viewer")

    # Collect all items grouped by date
    items_by_date = defaultdict(list)
    for stop in trip.stops:
        for item in stop.itinerary_items:
            if item.scheduled_date and item.start_time and item.end_time:
                items_by_date[item.scheduled_date].append((stop, item))

    conflicts = []
    for d, items in items_by_date.items():
        n = len(items)
        for i in range(n):
            for j in range(i + 1, n):
                stop_a, a = items[i]
                stop_b, b = items[j]

                # Check overlap
                if a.start_time < b.end_time and a.end_time > b.start_time:
                    # Calculate overlap minutes
                    dt_a_start = datetime.combine(d, a.start_time)
                    dt_a_end = datetime.combine(d, a.end_time)
                    dt_b_start = datetime.combine(d, b.start_time)
                    dt_b_end = datetime.combine(d, b.end_time)

                    overlap_start = max(dt_a_start, dt_b_start)
                    overlap_end = min(dt_a_end, dt_b_end)
                    overlap_minutes = int((overlap_end - overlap_start).total_seconds() / 60)

                    conflicts.append(
                        ConflictDetailOut(
                            date=d.isoformat(),
                            city=stop_a.city.name if stop_a.city else "Unknown",
                            item_a=ConflictItemInfo(
                                name=a.activity.name if a.activity else "Activity",
                                start=a.start_time.strftime("%H:%M"),
                                end=a.end_time.strftime("%H:%M"),
                            ),
                            item_b=ConflictItemInfo(
                                name=b.activity.name if b.activity else "Activity",
                                start=b.start_time.strftime("%H:%M"),
                                end=b.end_time.strftime("%H:%M"),
                            ),
                            overlap_minutes=max(1, overlap_minutes),
                        )
                    )

    return {
        "trip_id": trip.id,
        "conflicts": conflicts,
        "total_conflicts": len(conflicts),
    }
