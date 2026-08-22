import math
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.models.trip import Trip
from app.models.stay import TripStay
from app.models.stop import TripStop
from app.models.transit import TransitLeg, TransitOption
from app.models.itinerary_item import ItineraryItem
from app.models.expense import Expense

DEFAULT_MEAL_RATE_PER_PERSON_PER_DAY = 800.0


class BudgetService:
    @classmethod
    async def calculate_authoritative_budget(
        cls, db: AsyncSession, trip_id: str, meal_rate_per_person_per_day: float = DEFAULT_MEAL_RATE_PER_PERSON_PER_DAY
    ) -> Dict[str, Any]:
        """
        The absolute single source of truth for budget computation.
        Reads selected TransitLegs, TripStays, ItineraryItems, and Expenses.
        """
        # Load trip and all required relationships
        result = await db.execute(
            select(Trip)
            .options(
                selectinload(Trip.transit_legs).selectinload(TransitLeg.selected_option),
                selectinload(Trip.stops).selectinload(TripStop.stay_info),
                selectinload(Trip.stops).selectinload(TripStop.itinerary_items),
                selectinload(Trip.expenses),
            )
            .where(Trip.id == trip_id)
        )
        trip = result.scalar_one_or_none()
        if not trip:
            return {}

        num_travelers = max(1, int(getattr(trip, "num_travelers", 1) or 1))
        
        # 1. TRANSPORT = sum(selected transit option total_estimated_cost)
        transport_cost = 0.0
        for leg in trip.transit_legs:
            if leg.selected_option:
                transport_cost += leg.selected_option.total_estimated_cost

        # 2. STAY = sum(trip_stays.total_cost)
        stay_cost = 0.0
        for stop in trip.stops:
            for ts in getattr(stop, "stay_info", []):
                stay_cost += ts.cost

        # 3. ACTIVITIES = sum(trip_activity estimated/selected cost)
        activities_cost = 0.0
        for stop in trip.stops:
            for item in getattr(stop, "itinerary_items", []):
                activities_cost += item.effective_cost * num_travelers

        # 4. FOOD = explicit meal policy (Estimated Food)
        days_diff = (trip.end_date - trip.start_date).days
        total_trip_days = max(1, days_diff if days_diff > 0 else 1)
        meals_cost = total_trip_days * num_travelers * meal_rate_per_person_per_day

        # 5. OTHER = sum from Expenses table
        other_cost = 0.0
        total_actual_cost = 0.0
        for exp in trip.expenses:
            other_cost += exp.amount
            if exp.is_actual:
                total_actual_cost += exp.amount

        total_estimated_cost = transport_cost + stay_cost + activities_cost + meals_cost + other_cost
        cost_per_person = total_estimated_cost / num_travelers if num_travelers > 0 else 0.0

        # Room Math Rule: 1-2 -> 1 room, 3-4 -> 2 rooms, 5-6 -> 3 rooms
        rooms_allocated = math.ceil(num_travelers / 2.0)
        
        # Determine budget status & warnings
        warnings = []
        is_over_budget = False
        if trip.budget_target:
            if total_estimated_cost > trip.budget_target:
                is_over_budget = True
                warnings.append(f"Trip estimated cost ({trip.currency} {total_estimated_cost:,.2f}) exceeds target ({trip.currency} {trip.budget_target:,.2f})")
        
        # Synchronize legacy total_budget field on trip object
        trip.total_budget = total_estimated_cost

        return {
            "trip_id": trip.id,
            "travelers": num_travelers,
            "rooms": rooms_allocated,
            "total_estimated_cost": total_estimated_cost,
            "total_actual_cost": total_actual_cost,
            "cost_per_person": cost_per_person,
            "currency": trip.currency,
            "meal_policy": {
                "rate_per_person_per_day": meal_rate_per_person_per_day,
                "label": "Estimated Food",
                "days": total_trip_days,
                "calculated_food": meals_cost,
            },
            "breakdown": {
                "transport": transport_cost,
                "stay": stay_cost,
                "activities": activities_cost,
                "food": meals_cost,
                "other": other_cost
            },
            "warnings": warnings,
            "is_over_budget": is_over_budget,
            "budget_target": trip.budget_target,
        }

