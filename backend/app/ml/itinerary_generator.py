from datetime import date, datetime, time, timedelta
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.controllers.trip_controller import get_trip_and_check_access
from app.models.activity import Activity
from app.models.itinerary_item import ItineraryItem
from app.models.stop import TripStop
from app.models.user import User
from app.schemas.itinerary_item import (
    GeneratedDayActivityOut,
    GeneratedDayOut,
    GeneratedItineraryOut,
    GenerateItineraryRequest,
)

PACE_ACTIVITY_MAP = {
    "relaxed": 2,
    "moderate": 3,
    "intensive": 5,
}


def fits_budget(cost: float, preference: str) -> bool:
    """Checks if activity estimated cost matches the budget bracket."""
    pref = preference.lower()
    if pref == "budget":
        return cost <= 20.0
    elif pref == "luxury":
        return cost >= 80.0
    else:  # mid-range
        return 20.0 <= cost <= 80.0


async def generate_ai_itinerary(
    db: AsyncSession,
    trip_id: str,
    current_user: User,
    payload: GenerateItineraryRequest,
) -> dict:
    """
    Rule-based AI Itinerary Generator:
    1. Loads all stops for the trip ordered by stop_order.
    2. Calculates activities needed per day based on pace:
       - relaxed: 2 / day
       - moderate: 3 / day
       - intensive: 5 / day
    3. Selects best-matching city activities based on interests and budget bracket.
    4. Automatically schedules time slots from 09:00 to 21:00 with:
       - 0.5hr travel buffer between activities
       - 1hr lunch break at 13:00 - 14:00
    5. Saves ItineraryItem records to database and returns generated schedule.
    """
    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="editor")

    acts_per_day = PACE_ACTIVITY_MAP.get(payload.pace.lower(), 3)
    user_interests = [i.lower().strip() for i in payload.interests]

    # Delete existing auto-generated itinerary items for clean re-generation
    for stop in trip.stops:
        for item in stop.itinerary_items:
            await db.delete(item)
    await db.flush()

    generated_days = []
    total_activities_count = 0
    estimated_total_cost = 0.0

    ordered_stops = sorted(trip.stops, key=lambda s: s.stop_order)

    for stop in ordered_stops:
        days_diff = (stop.departure_date - stop.arrival_date).days
        days_at_stop = max(1, days_diff if days_diff > 0 else 1)
        total_needed = days_at_stop * acts_per_day

        # Fetch all activities for this city
        res = await db.execute(select(Activity).where(Activity.city_id == stop.city_id))
        all_city_acts = list(res.scalars().all())

        if not all_city_acts:
            continue

        # Score activities based on interest matching and budget fit
        def score_activity(act: Activity) -> float:
            score = 0.0
            act_cat = (act.category or "").lower()
            if any(interest in act_cat or act_cat in interest for interest in user_interests):
                score += 10.0
            if fits_budget(act.estimated_cost, payload.budget_preference):
                score += 5.0
            # Tie breaker: popularity / duration reasonable
            score += min(5.0, act.duration_hours)
            return score

        sorted_acts = sorted(all_city_acts, key=score_activity, reverse=True)

        # Ensure we have enough activities by cycling if catalog is small
        chosen_activities = []
        while len(chosen_activities) < total_needed and sorted_acts:
            for act in sorted_acts:
                chosen_activities.append(act)
                if len(chosen_activities) == total_needed:
                    break

        # Distribute activities across days
        act_index = 0
        for day_offset in range(days_at_stop):
            current_date = stop.arrival_date + timedelta(days=day_offset)
            current_time = datetime.combine(current_date, time(9, 0))  # Start at 09:00
            day_acts = []
            day_cost = 0.0
            day_hours = 0.0

            for _ in range(acts_per_day):
                if act_index >= len(chosen_activities):
                    break

                act = chosen_activities[act_index]
                act_index += 1

                # Handle lunch break at 13:00 - 14:00
                lunch_start = datetime.combine(current_date, time(13, 0))
                lunch_end = datetime.combine(current_date, time(14, 0))

                duration = timedelta(hours=act.duration_hours)
                proposed_end = current_time + duration

                # If current time is before lunch but overlaps lunch, or current time is in lunch
                if (current_time < lunch_start and proposed_end > lunch_start) or (lunch_start <= current_time < lunch_end):
                    current_time = lunch_end

                start_t = current_time.time()
                end_dt = min(current_time + duration, datetime.combine(current_date, time(21, 0)))
                end_t = end_dt.time()

                # Next activity time includes 0.5hr travel
                current_time = end_dt + timedelta(minutes=30)

                # Create DB ItineraryItem
                item = ItineraryItem(
                    trip_stop_id=stop.id,
                    activity_id=act.id,
                    scheduled_date=current_date,
                    start_time=start_t,
                    end_time=end_t,
                    custom_cost=act.estimated_cost,
                    notes=f"Auto-generated for pace '{payload.pace}' and interests '{', '.join(payload.interests)}'",
                    status="planned",
                )
                db.add(item)

                day_acts.append(
                    GeneratedDayActivityOut(
                        activity_id=act.id,
                        name=act.name,
                        start_time=start_t.strftime("%H:%M"),
                        end_time=end_t.strftime("%H:%M"),
                        estimated_cost=float(act.estimated_cost),
                        category=act.category,
                    )
                )
                day_cost += act.estimated_cost
                day_hours += act.duration_hours
                total_activities_count += 1
                estimated_total_cost += act.estimated_cost

            generated_days.append(
                GeneratedDayOut(
                    date=current_date.isoformat(),
                    city=stop.city.name if stop.city else "City",
                    activities=day_acts,
                    day_total_cost=round(day_cost, 2),
                    day_total_hours=round(day_hours, 1),
                )
            )

    await db.flush()

    return {
        "trip_id": trip.id,
        "generated_days": generated_days,
        "total_activities": total_activities_count,
        "estimated_total_cost": round(estimated_total_cost, 2),
    }
