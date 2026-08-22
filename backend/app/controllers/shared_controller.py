import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.controllers.trip_controller import duplicate_trip, get_trip_and_check_access
from app.models.activity import Activity
from app.models.itinerary_item import ItineraryItem
from app.models.shared_link import SharedLink
from app.models.stop import TripStop
from app.models.trip import Trip
from app.models.user import User
from app.schemas.city import CityOut
from app.schemas.shared_link import (
    SharedActivityOut,
    SharedLinkOut,
    SharedStopOut,
    SharedTripViewOut,
)


async def create_shared_link(
    db: AsyncSession,
    trip_id: str,
    current_user: User,
    expires_in_days: Optional[int] = 7,
) -> SharedLink:
    """Generates a secure share token for a trip."""
    await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="editor")

    expires_at = None
    if expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

    link = SharedLink(
        trip_id=trip_id,
        share_token=secrets.token_urlsafe(16),
        expires_at=expires_at,
    )
    db.add(link)
    await db.flush()
    await db.refresh(link)
    return link


async def get_shared_trip(db: AsyncSession, token: str) -> dict:
    """
    Public read-only view of a shared itinerary:
    - 404 if token not found or expired
    - Conforms to privacy rules (hides private notes and actual expense amounts)
    """
    res = await db.execute(
        select(SharedLink)
        .options(
            selectinload(SharedLink.trip)
            .selectinload(Trip.stops)
            .selectinload(TripStop.city),
            selectinload(SharedLink.trip)
            .selectinload(Trip.stops)
            .selectinload(TripStop.itinerary_items)
            .selectinload(ItineraryItem.activity),
        )
        .where(SharedLink.share_token == token)
    )
    link = res.scalar_one_or_none()

    if link is None or link.is_expired:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared trip link not found or has expired",
        )

    trip = link.trip
    days_diff = (trip.end_date - trip.start_date).days
    total_days = max(1, days_diff if days_diff > 0 else 1)

    stops_out = []
    for s in trip.stops:
        acts = []
        for it in s.itinerary_items:
            if it.activity:
                acts.append(
                    SharedActivityOut(
                        activity_id=it.activity.id,
                        name=it.activity.name,
                        category=it.activity.category,
                        duration_hours=it.activity.duration_hours,
                        estimated_cost=it.effective_cost,
                        scheduled_date=it.scheduled_date,
                        start_time=it.start_time.strftime("%H:%M") if it.start_time else None,
                        end_time=it.end_time.strftime("%H:%M") if it.end_time else None,
                    )
                )

        stops_out.append(
            SharedStopOut(
                stop_id=s.id,
                city=CityOut.model_validate(s.city),
                arrival_date=s.arrival_date,
                departure_date=s.departure_date,
                stop_order=s.stop_order,
                activities=acts,
            )
        )

    return {
        "trip_id": trip.id,
        "title": trip.title,
        "description": trip.description,
        "start_date": trip.start_date,
        "end_date": trip.end_date,
        "cover_photo": trip.cover_photo,
        "stops": stops_out,
        "total_days": total_days,
    }


async def copy_shared_trip(db: AsyncSession, token: str, current_user: User) -> Trip:
    """Copies a shared trip to the authenticated user's account as a draft."""
    res = await db.execute(select(SharedLink).where(SharedLink.share_token == token))
    link = res.scalar_one_or_none()

    if link is None or link.is_expired:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared trip link not found or has expired",
        )

    return await duplicate_trip(db=db, trip_id=link.trip_id, current_user=current_user)
