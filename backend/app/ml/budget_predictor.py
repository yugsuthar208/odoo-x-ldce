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
from app.ml.train import encode_region, train_and_save_model
from app.models.stop import Stop
from app.models.stop_activity import StopActivity
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
    Predicts the expected total budget for a planned trip using the trained Linear Regression model.
    Extracts:
      - total_days: integer duration between start_date and end_date
      - num_stops: count of stops scheduled
      - num_activities: count of activities scheduled
      - avg_city_cost_index: mean cost index across stop cities
      - region_encoded: encoded geographic region
    """
    # 1. Fetch trip and related data
    query = (
        select(Trip)
        .options(
            selectinload(Trip.stops).selectinload(Stop.city),
            selectinload(Trip.stops).selectinload(Stop.stop_activities),
        )
        .where(Trip.id == trip_id)
    )
    result = await db.execute(query)
    trip = result.scalar_one_or_none()

    if trip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id '{trip_id}' not found",
        )

    if trip.user_id != current_user.id and not trip.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this trip",
        )

    # 2. Extract features
    days_diff = (trip.end_date - trip.start_date).days
    total_days = max(1, days_diff if days_diff > 0 else 1)
    num_stops = len(trip.stops)

    total_activities = sum(len(stop.stop_activities) for stop in trip.stops)

    if trip.stops:
        city_costs = [stop.city.cost_index for stop in trip.stops if stop.city]
        avg_city_cost = float(np.mean(city_costs)) if city_costs else 100.0
        # Region from the first stop city
        first_city = trip.stops[0].city
        region_encoded = encode_region(first_city.region if first_city else "Europe")
    else:
        avg_city_cost = 100.0
        region_encoded = 0

    features_dict = {
        "total_days": int(total_days),
        "num_stops": int(num_stops),
        "num_activities": int(total_activities),
        "avg_city_cost_index": float(round(avg_city_cost, 2)),
        "region_encoded": int(region_encoded),
    }

    # 3. Model Inference
    model = get_or_load_model()
    input_df = pd.DataFrame([features_dict])
    prediction = model.predict(input_df)[0]
    predicted_cost = float(round(max(50.0, prediction), 2))

    return {
        "trip_id": trip.id,
        "predicted_total_cost": predicted_cost,
        "features_used": features_dict,
    }
