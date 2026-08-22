import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.trip import Trip
from app.models.transit import TransitLeg, TransitOption
from app.models.stay import TripStay
from app.models.recommendation import Recommendation, MLPrediction
from app.services.budget_service import BudgetService


class RecommendationService:
    @classmethod
    async def generate_budget_optimizations(cls, db: AsyncSession, trip: Trip) -> Dict[str, Any]:
        """
        Analyzes the trip's current authoritative budget against target budget.
        Generates non-mutating recommendations for savings (e.g. switching flight to train, or selecting cheaper stay).
        """
        budget_data = await BudgetService.calculate_authoritative_budget(db, trip.id)
        current_total = budget_data.get("total_estimated_cost", 0.0)
        target = trip.budget_target or current_total

        recommendations = []

        # 1. Analyze Transit Legs for potential savings
        result = await db.execute(
            select(TransitLeg)
            .options(selectinload(TransitLeg.options), selectinload(TransitLeg.selected_option))
            .where(TransitLeg.trip_id == trip.id)
        )
        legs = result.scalars().all()

        for leg in legs:
            if leg.selected_option and leg.options:
                current_cost = leg.selected_option.total_estimated_cost
                # Find cheaper option if available
                cheaper_options = [opt for opt in leg.options if opt.id != leg.selected_option.id and opt.total_estimated_cost < current_cost]
                if cheaper_options:
                    cheapest = min(cheaper_options, key=lambda o: o.total_estimated_cost)
                    saving = current_cost - cheapest.total_estimated_cost
                    if saving > 0:
                        rec_id = str(uuid.uuid4())
                        rec = Recommendation(
                            id=rec_id,
                            user_id=trip.user_id,
                            trip_id=trip.id,
                            rec_type="transit_optimization",
                            entity_type="TransitLeg",
                            entity_id=leg.id,
                            title=f"Switch transit to {cheapest.mode.title()} ({cheapest.provider or 'Standard'})",
                            reason=f"Switching from {leg.selected_option.mode.title()} ({leg.selected_option.provider or 'Current'}) saves {trip.currency} {saving:,.2f}.",
                            explanation=f"Switching from {leg.selected_option.mode.title()} to {cheapest.mode.title()} reduces travel costs.",
                            current_cost=current_cost,
                            alternative_cost=cheapest.total_estimated_cost,
                            estimated_saving=saving,
                            affected_entity="TransitLeg",
                            affected_entity_id=leg.id,
                            action_payload={
                                "action": "select_transit",
                                "leg_id": leg.id,
                                "option_id": cheapest.id,
                            },
                            score=0.9,
                            source="rule_engine",
                        )
                        db.add(rec)
                        recommendations.append({
                            "id": rec.id,
                            "title": rec.title,
                            "explanation": rec.reason,
                            "why": f"Fits your trip duration and saves {trip.currency} {saving:,.2f} on transport without impacting stop stay dates.",
                            "current_cost": current_cost,
                            "alternative_cost": cheapest.total_estimated_cost,
                            "estimated_saving": saving,
                            "affected_entity": "TransitLeg",
                            "affected_entity_id": leg.id,
                            "action_payload": rec.action_payload,
                        })

        await db.flush()

        return {
            "trip_id": trip.id,
            "current_total": current_total,
            "target": target,
            "recommendations": recommendations,
        }

    @classmethod
    async def apply_recommendation(cls, db: AsyncSession, trip_id: str, recommendation_id: str) -> Dict[str, Any]:
        """
        Applies a recommendation to the trip (e.g. updating transit choice or stay choice)
        and returns updated trip + budget.
        """
        rec = await db.get(Recommendation, recommendation_id)
        if not rec or rec.trip_id != trip_id:
            raise ValueError(f"Recommendation with id '{recommendation_id}' not found for trip '{trip_id}'")

        payload = rec.action_payload or {}
        action = payload.get("action")

        if action == "select_transit":
            leg_id = payload.get("leg_id")
            option_id = payload.get("option_id")
            leg = await db.get(TransitLeg, leg_id)
            if leg and leg.trip_id == trip_id:
                leg.selected_option_id = option_id
                db.add(leg)

        await db.flush()

        # Recalculate authoritative budget
        updated_budget = await BudgetService.calculate_authoritative_budget(db, trip_id)

        return {
            "message": f"Applied recommendation: {rec.title}",
            "recommendation_id": recommendation_id,
            "updated_budget": updated_budget,
        }
