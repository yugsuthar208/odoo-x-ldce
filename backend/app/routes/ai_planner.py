from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.services.ai_planner_service import AIPlannerService

router = APIRouter(prefix="/ai-planner", tags=["AI Trip Planner"])


class GenerateAIPlanRequest(BaseModel):
    origin_city: Optional[str] = "Mumbai"
    destination_input: str = Field(..., description="Destination city or circuit, e.g. 'Gandhinagar', 'Jaipur, Udaipur'")
    duration_days: int = Field(5, ge=1, le=30, description="Total days for the trip")
    travelers: int = Field(2, ge=1, le=20, description="Number of travelers")
    budget_tier: str = Field("mid", description="budget, mid, luxury")
    travel_style: str = Field("explorer", description="explorer, romantic, luxury, adventure, family")
    transit_preference: str = Field("train", description="train, flight, road, bus, cab, optimal")
    dietary_preference: str = Field("all", description="all, vegetarian, authentic_regional, street_food, fine_dining")
    interests: List[str] = Field(default_factory=lambda: ["heritage", "food", "nature", "sightseeing"])
    start_date: Optional[str] = None


class SaveAITripRequest(BaseModel):
    ai_blueprint: Dict[str, Any]


@router.post(
    "/generate",
    response_model=APIResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Generate Master AI Travel Blueprint",
)
async def generate_ai_trip_plan(
    payload: GenerateAIPlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Synthesizes a complete travel master blueprint:
    - Time-blocked day-by-day itinerary (08:30 to 21:30)
    - Real-world map coordinates and mode-aware routing
    - Regional 'Must-Eat' culinary recommendations & iconic spots
    - Multi-modal transport options and stay recommendations
    - Authoritative INR cost forecast
    """
    blueprint = await AIPlannerService.generate_master_itinerary(
        db=db,
        origin_city=payload.origin_city,
        destination_input=payload.destination_input,
        duration_days=payload.duration_days,
        travelers=payload.travelers,
        budget_tier=payload.budget_tier,
        travel_style=payload.travel_style,
        transit_preference=payload.transit_preference,
        dietary_preference=payload.dietary_preference,
        interests=payload.interests,
        start_date_str=payload.start_date,
    )

    return APIResponse(
        success=True,
        data=blueprint,
        message="Master AI Itinerary generated successfully",
    )


@router.post(
    "/save-trip",
    response_model=APIResponse[Dict[str, Any]],
    status_code=status.HTTP_201_CREATED,
    summary="1-Click Save AI Itinerary as an Active Trip in Database",
)
async def save_ai_trip(
    payload: SaveAITripRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Persists the AI generated blueprint into actual database Trip, Stops, Activities,
    Transit Legs, and Budget records so it appears directly in 'My Trips'.
    """
    created_trip = await AIPlannerService.save_ai_trip_to_database(
        db=db,
        current_user=current_user,
        ai_blueprint=payload.ai_blueprint,
    )

    return APIResponse(
        success=True,
        data={"trip_id": created_trip.id, "title": created_trip.title},
        message="AI Itinerary saved to database as an active trip successfully",
    )
