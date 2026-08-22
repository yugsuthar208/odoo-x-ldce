from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.recommendation import MLPrediction


class MLService:
    @classmethod
    async def record_prediction(
        cls,
        db: AsyncSession,
        prediction_type: str,
        predicted_value: float,
        input_features: Dict[str, Any],
        prediction_details: Dict[str, Any],
        trip_id: Optional[str] = None,
        user_id: Optional[str] = None,
        model_name: str = "budget_xgboost",
        model_version: str = "1.0.0",
    ) -> MLPrediction:
        """
        Persists a meaningful ML prediction record to the database for auditing and personalize history.
        """
        record = MLPrediction(
            user_id=user_id,
            trip_id=trip_id,
            model_name=model_name,
            model_version=model_version,
            prediction_type=prediction_type,
            predicted_value=predicted_value,
            input_features=input_features,
            prediction=prediction_details,
            features_used=input_features,
            created_at=datetime.utcnow(),
        )
        db.add(record)
        await db.flush()
        return record
