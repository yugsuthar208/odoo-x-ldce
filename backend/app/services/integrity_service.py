from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.models.trip import Trip, TripStatus
from app.models.stop import TripStop
from app.models.transit import TransitLeg
from app.models.stay import TripStay
from app.models.itinerary_item import ItineraryItem
from app.services.budget_service import BudgetService


class IntegrityService:
    """
    Authoritative Trip Integrity Service for production hardening & readiness validation.
    Performs comprehensive checks before allowing DRAFT -> PLANNING -> READY state progression.
    """

    @staticmethod
    async def validate_trip_integrity(db: AsyncSession, trip_id: str) -> Dict[str, Any]:
        """
        Validates full trip integrity across dates, stops ordering, transit legs, stays,
        scheduled activities, time conflicts, and authoritative budget aggregation.
        """
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Fetch Trip with all relations loaded
        stmt = (
            select(Trip)
            .options(
                selectinload(Trip.stops).selectinload(TripStop.stay_info),
                selectinload(Trip.stops).selectinload(TripStop.itinerary_items),
                selectinload(Trip.transit_legs).selectinload(TransitLeg.selected_option),
            )
            .where(Trip.id == trip_id)
        )
        res = await db.execute(stmt)
        trip = res.scalar_one_or_none()

        if not trip:
            return {
                "ready": False,
                "status": "NOT_FOUND",
                "trip_id": trip_id,
                "errors": ["Trip not found."],
                "warnings": [],
            }

        # 2. Date Bounds Check
        if not trip.start_date or not trip.end_date:
            errors.append("Trip must have valid start_date and end_date.")
        elif trip.start_date >= trip.end_date:
            errors.append(f"Trip start_date ({trip.start_date}) must be strictly before end_date ({trip.end_date}).")

        # 3. Stops Ordering & Date Validation
        stops = trip.stops or []
        if len(stops) == 0:
            warnings.append("Trip has no stops added.")
        else:
            # Check sequential ordering
            expected_order = 0
            for s in sorted(stops, key=lambda x: x.stop_order):
                if s.arrival_date and s.departure_date and s.arrival_date >= s.departure_date:
                    errors.append(f"Stop '{s.id}' arrival_date ({s.arrival_date}) must be before departure_date ({s.departure_date}).")
                
                if trip.start_date and s.arrival_date and s.arrival_date < trip.start_date:
                    errors.append(f"Stop '{s.id}' arrival ({s.arrival_date}) is before trip start date ({trip.start_date}).")
                
                if trip.end_date and s.departure_date and s.departure_date > trip.end_date:
                    errors.append(f"Stop '{s.id}' departure ({s.departure_date}) is after trip end date ({trip.end_date}).")

            # Check overlapping stops
            sorted_stops = sorted(stops, key=lambda x: (x.arrival_date or trip.start_date, x.stop_order))
            for i in range(len(sorted_stops) - 1):
                cur_stop = sorted_stops[i]
                next_stop = sorted_stops[i + 1]
                if cur_stop.departure_date and next_stop.arrival_date and cur_stop.departure_date > next_stop.arrival_date:
                    errors.append(f"Stop order conflict between stop {cur_stop.id} and stop {next_stop.id}.")

        # 4. Transit Legs Check
        transit_legs = trip.transit_legs or []
        num_expected_legs = max(0, len(stops) - 1)
        if len(stops) >= 2 and len(transit_legs) < num_expected_legs:
            errors.append(f"Expected {num_expected_legs} transit legs between {len(stops)} stops, but found {len(transit_legs)}.")

        selected_transit_count = 0
        for leg in transit_legs:
            if leg.selected_option_id and leg.selected_option:
                selected_transit_count += 1
            else:
                warnings.append(f"Transit leg '{leg.id}' from stop {leg.origin_stop_id} to {leg.destination_stop_id} has no selected transit option.")

        # 5. Stays Check
        stay_count = 0
        for s in stops:
            stays_for_stop = getattr(s, "stay_info", []) or []
            stay_count += len(stays_for_stop)
            for stay in stays_for_stop:
                if stay.checkin_date and stay.checkout_date and stay.checkin_date >= stay.checkout_date:
                    errors.append(f"Stay '{stay.id}' check-in date must be before check-out date.")

        # 6. Scheduled Activities & Conflict Detection
        activity_count = 0
        scheduled_times_by_date = {}
        for s in stops:
            items = getattr(s, "itinerary_items", []) or []
            activity_count += len(items)
            for item in items:
                # Check scheduled date bounds
                if item.scheduled_date:
                    if s.arrival_date and item.scheduled_date < s.arrival_date:
                        errors.append(f"Activity item '{item.id}' date ({item.scheduled_date}) is before stop arrival date ({s.arrival_date}).")
                    if s.departure_date and item.scheduled_date > s.departure_date:
                        errors.append(f"Activity item '{item.id}' date ({item.scheduled_date}) is after stop departure date ({s.departure_date}).")
                
                # Check time overlaps on same date
                if item.scheduled_date and item.start_time and item.end_time:
                    date_key = str(item.scheduled_date)
                    if date_key not in scheduled_times_by_date:
                        scheduled_times_by_date[date_key] = []
                    
                    # Convert to minutes past midnight for overlap check
                    try:
                        sh, sm = map(int, str(item.start_time).split(":")[:2])
                        eh, em = map(int, str(item.end_time).split(":")[:2])
                        start_mins = sh * 60 + sm
                        end_mins = eh * 60 + em
                        
                        for existing_start, existing_end, existing_title in scheduled_times_by_date[date_key]:
                            if max(start_mins, existing_start) < min(end_mins, existing_end):
                                warnings.append(f"Schedule conflict on {date_key}: Activity overlaps with existing item.")
                        
                        scheduled_times_by_date[date_key].append((start_mins, end_mins, item.id))
                    except Exception:
                        pass

        # 7. Authoritative Budget Calculation
        authoritative_budget = await BudgetService.calculate_authoritative_budget(db, trip_id)

        # Readiness Flag: True if 0 blocking errors
        is_ready = len(errors) == 0

        return {
            "ready": is_ready,
            "status": trip.status,
            "trip_id": trip.id,
            "title": trip.title,
            "stops": len(stops),
            "transit_legs": len(transit_legs),
            "selected_transit_legs": selected_transit_count,
            "stays": stay_count,
            "activities": activity_count,
            "budget": {
                "transport": authoritative_budget.get("breakdown", {}).get("transport", 0.0),
                "stay": authoritative_budget.get("breakdown", {}).get("stay", 0.0),
                "food": authoritative_budget.get("breakdown", {}).get("food", 0.0),
                "activities": authoritative_budget.get("breakdown", {}).get("activities", 0.0),
                "other": authoritative_budget.get("breakdown", {}).get("other", 0.0),
                "total": authoritative_budget.get("total_estimated_cost", 0.0),
                "per_person": authoritative_budget.get("cost_per_person", 0.0),
                "currency": authoritative_budget.get("currency", "INR"),
            },
            "errors": errors,
            "warnings": warnings,
        }
