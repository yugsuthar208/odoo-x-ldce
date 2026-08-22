from datetime import date
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.stay import Stay, TripStay
from app.models.stop import TripStop
from app.models.city import City


class StayService:
    @classmethod
    async def get_city_stays(cls, db: AsyncSession, city_id: str) -> List[Stay]:
        """Fetches catalog of stays for a specific city."""
        result = await db.execute(
            select(Stay).where(Stay.city_id == city_id).order_by(Stay.name.asc())
        )
        return list(result.scalars().all())

    @classmethod
    async def select_trip_stay(
        cls,
        db: AsyncSession,
        trip_stop_id: str,
        name: str,
        checkin_date: date,
        checkout_date: date,
        nightly_cost: float,
        stay_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> TripStay:
        """
        Creates or updates a TripStay for a stop.
        Calculates authoritative total stay cost based on nightly cost * night count.
        """
        nights = max(1, (checkout_date - checkin_date).days)
        total_cost = round(nightly_cost * nights, 2)

        # Fetch existing TripStay if present
        res = await db.execute(
            select(TripStay).where(TripStay.trip_stop_id == trip_stop_id)
        )
        trip_stay = res.scalar_one_or_none()

        if trip_stay is None:
            stop = await db.get(TripStop, trip_stop_id)
            trip_id = stop.trip_id if stop else None

            trip_stay = TripStay(
                trip_stop_id=trip_stop_id,
                trip_id=trip_id,
                stay_id=stay_id,
                name=name,
                checkin_date=checkin_date,
                checkout_date=checkout_date,
                nightly_cost=nightly_cost,
                cost=total_cost,
                notes=notes,
            )
            db.add(trip_stay)
        else:
            trip_stay.stay_id = stay_id
            trip_stay.name = name
            trip_stay.checkin_date = checkin_date
            trip_stay.checkout_date = checkout_date
            trip_stay.nightly_cost = nightly_cost
            trip_stay.cost = total_cost
            if notes is not None:
                trip_stay.notes = notes
            db.add(trip_stay)

        await db.flush()
        return trip_stay
