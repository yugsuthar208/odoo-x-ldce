from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.ml.budget_predictor import predict_trip_budget
from app.ml.recommender import recommend_cities_for_user
from app.models.user import User
from app.schemas.budget import PredictedBudgetOut
from app.schemas.city import CityOut
from app.schemas.common import APIResponse

router = APIRouter(prefix="/recommend", tags=["ML & Recommendations"])


@router.get(
    "/cities",
    response_model=APIResponse[List[CityOut]],
    status_code=status.HTTP_200_OK,
    summary="Recommend destination cities for current user",
)
async def get_recommended_cities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Recommends personalized travel destinations based on the traveler's past trip history
    using Content-Based Cosine Similarity on cost index, popularity score, and region features.
    If the traveler has no trip history, returns top cities ranked by popularity.
    """
    recommended_cities = await recommend_cities_for_user(db=db, current_user=current_user, top_n=5)
    return APIResponse(
        success=True,
        data=recommended_cities,
        message="Personalized city recommendations generated successfully",
    )


@router.get(
    "/budget/{trip_id}",
    response_model=APIResponse[PredictedBudgetOut],
    status_code=status.HTTP_200_OK,
    summary="Predict trip budget using Machine Learning",
)
async def get_predicted_trip_budget(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Predicts the expected total expenditure for a trip using a trained Scikit-Learn Linear Regression model.
    Takes into account trip duration, number of stops, scheduled activities, average destination cost index, and region.
    """
    prediction_result = await predict_trip_budget(db=db, trip_id=trip_id, current_user=current_user)
    return APIResponse(
        success=True,
        data=prediction_result,
        message="Trip budget predicted successfully using machine learning model",
    )
