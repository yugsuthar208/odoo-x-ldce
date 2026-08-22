from datetime import date
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.controllers.trip_controller import calculate_trip_budget, get_trip_and_check_access
from app.database import get_db
from app.middleware.auth import get_current_user
from app.ml.budget_predictor import BudgetPredictor
from app.ml.recommender import HybridRecommender
from app.models.activity import Activity
from app.models.city import City
from app.models.stop import TripStop
from app.models.trip import Trip
from app.models.user import User
from app.schemas.common import APIResponse

router = APIRouter(prefix="/recommend", tags=["ML & AI Recommendations"])


def get_ml_models(request: Request):
    """Retrieves preloaded ML models from app.state or initializes fallback."""
    budget_predictor = getattr(request.app.state, "budget_predictor", None)
    recommender = getattr(request.app.state, "recommender", None)

    if budget_predictor is None or not budget_predictor.is_loaded:
        bp = BudgetPredictor()
        if bp.load():
            request.app.state.budget_predictor = bp
            budget_predictor = bp

    if recommender is None or not recommender.is_loaded:
        hr = HybridRecommender()
        if hr.load():
            request.app.state.recommender = hr
            recommender = hr

    return budget_predictor, recommender


@router.get(
    "/cities",
    response_model=APIResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="3-Layer Hybrid City Recommendations",
)
async def get_recommended_cities(
    request: Request,
    interests: Optional[str] = Query(None, description="Comma-separated interests (e.g. 'history,food,beaches')"),
    budget: Optional[float] = Query(None, description="Total budget in USD"),
    travel_month: Optional[int] = Query(None, ge=1, le=12, description="Month of travel (1-12)"),
    duration_days: Optional[int] = Query(7, ge=1, description="Trip duration in days"),
    num_travelers: Optional[int] = Query(1, ge=1, description="Number of travelers"),
    travel_style: Optional[str] = Query("explorer", description="backpacker, explorer, luxury"),
    vibes: Optional[str] = Query(None, description="Comma-separated vibes (e.g. 'romantic,relaxed')"),
    climate_pref: Optional[str] = Query("any", description="tropical, mediterranean, continental, arid, oceanic, any"),
    exclude_visited: Optional[bool] = Query(True, description="Exclude cities user has already visited in past trips"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    3-Layer Hybrid Destination Recommendation:
      - Layer 1: SentenceTransformer all-MiniLM-L6-v2 Semantic Embeddings
      - Layer 2: Multi-Criteria Composite Scoring Engine (Interest Match, Budget Fit, Seasonality, Safety)
      - Layer 3: Collaborative Filtering K-Means Archetype Affinity Boost
    """
    _, recommender = get_ml_models(request)

    if recommender is None or not recommender.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML models not yet trained. Please run training pipeline.",
        )

    # 1. Fetch all candidate cities from DB
    res = await db.execute(select(City))
    all_cities_db = list(res.scalars().all())

    # 2. Extract visited cities if exclude_visited is True
    visited_city_ids = set()
    user_trip_history = []
    user_trips_res = await db.execute(
        select(Trip).options(selectinload(Trip.stops)).where(Trip.user_id == current_user.id)
    )
    user_trips = list(user_trips_res.scalars().all())
    for t in user_trips:
        user_trip_history.append({"total_budget": t.total_budget, "duration": (t.end_date - t.start_date).days})
        for s in t.stops:
            if s.city_id:
                visited_city_ids.add(s.city_id)

    candidate_cities = []
    for c in all_cities_db:
        if exclude_visited and c.id in visited_city_ids and len(all_cities_db) > len(visited_city_ids):
            continue

        c_dict = {
            "id": c.id,
            "name": c.name,
            "country": c.country,
            "region": c.region,
            "tags": c.tags or [],
            "vibe_tags": c.vibe_tags or [],
            "climate_type": c.climate_type or "temperate",
            "best_months": c.best_months or [],
            "safety_index": c.safety_index if c.safety_index is not None else 75.0,
            "budget_tier": c.budget_tier or "mid-range",
            "cost_index": c.cost_index,
            "popularity_score": c.popularity_score,
        }
        candidate_cities.append(c_dict)

    query_dict = {
        "interests": interests or "sightseeing, culture, food",
        "budget": budget or 2500.0,
        "travel_month": travel_month or date.today().month,
        "duration_days": duration_days,
        "num_travelers": num_travelers,
        "travel_style": travel_style,
        "vibes": vibes or "vibrant, cultural",
        "climate_pref": climate_pref,
    }

    rec_result = recommender.recommend_cities(
        user_query=query_dict,
        candidate_cities=candidate_cities,
        user_trip_history=user_trip_history,
        top_n=5,
    )
    rec_result["excluded_visited"] = len(visited_city_ids) if exclude_visited else 0

    return APIResponse(
        success=True,
        data=rec_result,
        message="Top 5 destinations recommended",
    )


@router.get(
    "/budget/{trip_id}",
    response_model=APIResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="XGBoost Trip Budget Predictor",
)
async def get_predicted_trip_budget(
    request: Request,
    trip_id: str,
    accommodation_tier: Optional[str] = Query("mid", description="budget, mid, luxury"),
    travel_style: Optional[str] = Query("explorer", description="backpacker, explorer, luxury"),
    activity_density: Optional[str] = Query("medium", description="low, medium, high"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    XGBoost Machine Learning Budget Predictor:
    Predicts trip expenditure accounting for accommodation tiers, peak seasonality, activity density,
    and flight distance benchmarks.
    """
    budget_predictor, _ = get_ml_models(request)

    if budget_predictor is None or not budget_predictor.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML models not yet trained. Please run training pipeline.",
        )

    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="viewer")

    days_diff = (trip.end_date - trip.start_date).days
    total_days = max(1, days_diff if days_diff > 0 else 1)
    travel_month = trip.start_date.month

    # Compute average cost index from stops
    if trip.stops:
        costs = [s.city.cost_index for s in trip.stops if s.city and s.city.cost_index is not None]
        avg_cost = float(sum(costs) / len(costs)) if costs else 75.0
        rents = [getattr(s.city, "rent_index", 45.0) or 45.0 for s in trip.stops if s.city]
        avg_rent = float(sum(rents) / len(rents)) if rents else 45.0
        rests = [getattr(s.city, "restaurant_price_index", 60.0) or 60.0 for s in trip.stops if s.city]
        avg_rest = float(sum(rests) / len(rests)) if rests else 60.0
    else:
        avg_cost = 75.0
        avg_rent = 45.0
        avg_rest = 60.0

    # Flight distance estimation (sum of distances or benchmark)
    flight_dist = 2500.0
    if len(trip.stops) >= 2:
        from app.controllers.trip_controller import calculate_map_route
        route_info = await calculate_map_route(db=db, trip_id=trip_id, current_user=current_user)
        flight_dist = max(500.0, float(route_info.get("total_distance_km", 2500.0)))

    season_str = "peak" if travel_month in [6, 7, 8, 12] else ("shoulder" if travel_month in [4, 5, 9, 10] else "off-peak")

    trip_features = {
        "cost_of_living_index": avg_cost,
        "rent_index": avg_rent,
        "restaurant_price_index": avg_rest,
        "travel_month": travel_month,
        "season": season_str,
        "duration_days": total_days,
        "num_travelers": 1,
        "accommodation_tier": accommodation_tier,
        "travel_style": travel_style,
        "activity_density": activity_density,
        "flight_distance_km": flight_dist,
        "num_stops": max(1, len(trip.stops)),
    }

    ml_prediction = budget_predictor.predict(trip_features)

    # Actual rule-based calculation
    calc_res = await calculate_trip_budget(trip_id=trip_id, current_user=current_user, db=db)
    calculated_cost = calc_res["cost_breakdown"]["total_cost"]

    return APIResponse(
        success=True,
        data={
            "trip_id": trip.id,
            "input_features": {
                "duration_days": total_days,
                "num_travelers": 1,
                "num_stops": len(trip.stops),
                "avg_cost_index": round(avg_cost, 1),
                "travel_month": travel_month,
                "season": season_str,
                "accommodation_tier": accommodation_tier,
                "travel_style": travel_style,
                "activity_density": activity_density,
                "flight_distance_km": round(flight_dist, 1),
            },
            "prediction": ml_prediction,
            "calculated_cost": calculated_cost,
            "variance_note": "ML prediction accounts for peak season pricing and accommodation tier. Rule-based calculation uses base cost index only.",
            "season_warning": ml_prediction.get("season_warning"),
            "feature_importance": ml_prediction.get("feature_importance"),
        },
        message="Budget predicted successfully",
    )


@router.get(
    "/activities/{trip_id}",
    response_model=APIResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Semantic Activity Recommendations per Stop",
)
async def get_recommended_activities_for_trip(
    request: Request,
    trip_id: str,
    interests: Optional[str] = Query(None, description="Comma-separated interests (e.g. 'food,museums,adventure')"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Ranks and suggests activities for each stop of the trip using SentenceTransformer semantic matching.
    """
    _, recommender = get_ml_models(request)

    if recommender is None or not recommender.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML models not yet trained. Please run training pipeline.",
        )

    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="viewer")

    user_interests_list = [i.strip() for i in (interests or "sightseeing, culture, food").split(",") if i.strip()]

    recommendations_by_stop = []

    for stop in trip.stops:
        scheduled_act_ids = {it.activity_id for it in stop.itinerary_items if it.activity_id}

        # Fetch all activities for this city
        res = await db.execute(select(Activity).where(Activity.city_id == stop.city_id))
        city_activities = list(res.scalars().all())

        candidate_acts = []
        for act in city_activities:
            if act.id not in scheduled_act_ids:
                candidate_acts.append({
                    "id": act.id,
                    "name": act.name,
                    "category": act.category,
                    "description": act.description,
                    "tags": act.tags or [act.category],
                    "estimated_cost": act.estimated_cost,
                    "duration_hours": act.duration_hours,
                })

        suggested = recommender.recommend_activities(
            user_interests=user_interests_list,
            activities=candidate_acts,
            budget_preference="mid-range",
            top_n=5,
        )

        recommendations_by_stop.append({
            "stop_id": stop.id,
            "city_name": stop.city.name if stop.city else "City",
            "suggested_activities": suggested,
        })

    return APIResponse(
        success=True,
        data={"recommendations_by_stop": recommendations_by_stop},
        message="Activity recommendations generated successfully for each stop",
    )
