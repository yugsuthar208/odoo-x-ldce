import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger("BudgetPredictor")

MODELS_DIR = Path(__file__).resolve().parent / "models"


class BudgetPredictor:
    """
    XGBoost-powered Trip Budget Predictor:
    Predicts realistic multi-city travel expenditure incorporating Numbeo city cost indices,
    seasonality multipliers, accommodation tiers, activity density, and flight distances.
    """

    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir or MODELS_DIR
        self.model = None
        self.scaler = None
        self.encoder = None
        self._is_loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded and self.model is not None

    def load(self) -> bool:
        """Loads trained XGBoost model and preprocessors from disk."""
        model_path = self.models_dir / "budget_model.pkl"
        scaler_path = self.models_dir / "budget_scaler.pkl"
        encoder_path = self.models_dir / "budget_encoder.pkl"

        if not model_path.exists():
            logger.warning(f"ML model not found at {model_path}. Run python app/ml/train.py first.")
            self._is_loaded = False
            return False

        try:
            self.model = joblib.load(model_path)
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
            if encoder_path.exists():
                self.encoder = joblib.load(encoder_path)
            self._is_loaded = True
            logger.info("✓ BudgetPredictor model and preprocessors loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load BudgetPredictor model: {e}")
            self._is_loaded = False
            return False

    def predict(self, trip_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs prediction for a travel itinerary configuration.
        """
        if not self.is_loaded:
            raise RuntimeError("BudgetPredictor is not loaded. Please train models first.")

        # Extract features with sensible defaults
        cost_of_living_index = float(trip_features.get("cost_of_living_index", 75.0))
        rent_index = float(trip_features.get("rent_index", 45.0))
        restaurant_price_index = float(trip_features.get("restaurant_price_index", 60.0))
        travel_month = int(trip_features.get("travel_month", 6))
        duration_days = max(1, int(trip_features.get("duration_days", 7)))
        num_travelers = max(1, int(trip_features.get("num_travelers", 1)))
        flight_distance_km = float(trip_features.get("flight_distance_km", 2000.0))
        num_stops = max(1, int(trip_features.get("num_stops", 1)))

        # Season mapping
        season_str = str(trip_features.get("season", "")).lower()
        if not season_str:
            if travel_month in [6, 7, 8, 12]:
                season_str = "peak"
            elif travel_month in [4, 5, 9, 10]:
                season_str = "shoulder"
            else:
                season_str = "off-peak"

        season_map = {"off-peak": 0, "off_peak": 0, "shoulder": 1, "peak": 2}
        season_encoded = season_map.get(season_str, 1)

        # Accommodation Tier mapping
        acc_str = str(trip_features.get("accommodation_tier", "mid")).lower()
        acc_map = {"budget": 0, "mid": 1, "mid-range": 1, "luxury": 2}
        acc_encoded = acc_map.get(acc_str, 1)

        # Travel Style mapping
        style_str = str(trip_features.get("travel_style", "explorer")).lower()
        style_map = {"backpacker": 0, "explorer": 1, "luxury": 2}
        style_encoded = style_map.get(style_str, 1)

        # Activity Density mapping
        density_str = str(trip_features.get("activity_density", "medium")).lower()
        density_map = {"low": 0, "medium": 1, "high": 2}
        density_encoded = density_map.get(density_str, 1)

        feature_cols = [
            "cost_of_living_index", "rent_index", "restaurant_price_index",
            "travel_month", "season_encoded", "duration_days", "num_travelers",
            "accommodation_tier_encoded", "travel_style_encoded", "activity_density_encoded",
            "flight_distance_km", "num_stops"
        ]

        raw_df = pd.DataFrame([{
            "cost_of_living_index": cost_of_living_index,
            "rent_index": rent_index,
            "restaurant_price_index": restaurant_price_index,
            "travel_month": travel_month,
            "season_encoded": season_encoded,
            "duration_days": duration_days,
            "num_travelers": num_travelers,
            "accommodation_tier_encoded": acc_encoded,
            "travel_style_encoded": style_encoded,
            "activity_density_encoded": density_encoded,
            "flight_distance_km": flight_distance_km,
            "num_stops": num_stops,
        }])

        X_input = raw_df[feature_cols]
        if self.scaler is not None:
            X_input = self.scaler.transform(X_input)

        predicted_val = float(self.model.predict(X_input)[0])
        predicted_cost = round(max(100.0, predicted_val), 2)

        # Confidence interval (+/- 15%)
        low_cost = round(predicted_cost * 0.85, 2)
        high_cost = round(predicted_cost * 1.15, 2)

        # Estimated category breakdown
        acc_ratio = 0.35 if acc_encoded == 1 else (0.25 if acc_encoded == 0 else 0.45)
        meal_ratio = 0.25 if style_encoded == 1 else (0.20 if style_encoded == 0 else 0.30)
        act_ratio = 0.18
        flight_ratio = max(0.10, 1.0 - (acc_ratio + meal_ratio + act_ratio))

        acc_est = round(predicted_cost * acc_ratio, 2)
        meal_est = round(predicted_cost * meal_ratio, 2)
        act_est = round(predicted_cost * act_ratio, 2)
        flight_est = round(predicted_cost * flight_ratio, 2)

        per_person = round(predicted_cost / num_travelers, 2)
        per_day = round(predicted_cost / duration_days, 2)

        season_warning = None
        if season_str == "peak":
            month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            m_name = month_names[travel_month - 1] if 1 <= travel_month <= 12 else "Peak season"
            season_warning = f"{m_name} is peak travel season. Costs may be 40-70% higher due to high seasonal demand."

        return {
            "predicted_total_cost": predicted_cost,
            "confidence_interval": {
                "low": low_cost,
                "high": high_cost,
            },
            "cost_breakdown_estimate": {
                "accommodation": acc_est,
                "meals": meal_est,
                "activities": act_est,
                "flights": flight_est,
            },
            "per_person_cost": per_person,
            "cost_per_day": per_day,
            "season_warning": season_warning,
            "feature_importance": {
                "accommodation_tier": "HIGH",
                "season": "HIGH",
                "flight_distance_km": "MEDIUM",
                "duration_days": "MEDIUM",
                "cost_of_living_index": "MEDIUM",
            },
        }
