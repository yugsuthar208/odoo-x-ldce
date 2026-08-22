import os
from pathlib import Path
from typing import Optional
from fastapi import HTTPException, status
import joblib
import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.controllers.trip_controller import calculate_trip_budget, get_trip_and_check_access
from app.ml.train import encode_region, train_and_save_model
from app.models.itinerary_item import ItineraryItem
from app.models.stop import TripStop
from app.models.trip import Trip
from app.models.user import User

_budget_model = None


def get_or_load_model():
    """Retrieves the cached LinearRegression model or loads/trains it on demand."""
    global _budget_model
    if _budget_model is not None:
        return _budget_model

    model_path = Path(settings.ML_MODEL_PATH)
    if not model_path.exists():
        print(f"[ML] Model file not found at {model_path}. Training a new model...")
        _budget_model = train_and_save_model(str(model_path))
    else:
        try:
            _budget_model = joblib.load(str(model_path))
            print(f"[ML] Budget model loaded successfully from {model_path}")
        except Exception as e:
            print(f"[ML] Error loading model ({e}). Re-training...")
            _budget_model = train_and_save_model(str(model_path))

    return _budget_model


async def predict_trip_budget(
    db: AsyncSession,
    trip_id: str,
    current_user: User,
) -> dict:
    """
    Predicts expected trip total expenditure using Linear Regression alongside actual calculated cost.
    Features:
      - total_days (int)
      - num_stops (int)
      - num_activities (int)
      - avg_city_cost_index (float)
      - total_activity_cost (float)
      - region_encoded (int)
    """
    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="viewer")

    days_diff = (trip.end_date - trip.start_date).days
    total_days = max(1, days_diff if days_diff > 0 else 1)
    num_stops = len(trip.stops)

    total_activities = 0
    total_act_cost = 0.0
    for stop in trip.stops:
        for it in stop.itinerary_items:
            total_activities += 1
            total_act_cost += it.effective_cost

    if trip.stops:
        city_costs = [stop.city.cost_index for stop in trip.stops if stop.city and stop.city.cost_index is not None]
        avg_city_cost = float(np.mean(city_costs)) if city_costs else settings.DEFAULT_CITY_COST_INDEX
        first_city = trip.stops[0].city
        region_encoded = encode_region(first_city.region if first_city else "Europe")
    else:
        avg_city_cost = settings.DEFAULT_CITY_COST_INDEX
        region_encoded = 0

    features_dict = {
        "total_days": int(total_days),
        "num_stops": int(num_stops),
        "num_activities": int(total_activities),
        "avg_city_cost_index": float(round(avg_city_cost, 2)),
        "total_activity_cost": float(round(total_act_cost, 2)),
        "region_encoded": int(region_encoded),
    }

    model = get_or_load_model()
    input_df = pd.DataFrame([features_dict])
    prediction = model.predict(input_df)[0]
    predicted_cost = float(round(max(100.0, prediction), 2))

    # Also compute actual calculated cost
    calc_result = await calculate_trip_budget(trip_id=trip_id, current_user=current_user, db=db)
    calculated_total = calc_result["cost_breakdown"]["total_cost"]

    return {
        "trip_id": trip.id,
        "predicted_total_cost": predicted_cost,
        "calculated_total_cost": calculated_total,
        "confidence_note": "Prediction based on trip features and machine learning regression",
        "features_used": {
            "total_days": int(total_days),
            "num_stops": int(num_stops),
            "num_activities": int(total_activities),
            "avg_city_cost_index": float(round(avg_city_cost, 2)),
        },
    }
