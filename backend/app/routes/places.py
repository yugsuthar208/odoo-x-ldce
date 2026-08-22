from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query, status

from app.schemas.common import APIResponse
from app.services.live_search_service import LiveSearchService

router = APIRouter(prefix="/places", tags=["Live Food & Stays Recommendations"])


@router.get(
    "/live-food",
    response_model=APIResponse[List[Dict[str, Any]]],
    status_code=status.HTTP_200_OK,
    summary="Live DuckDuckGo authentic food & restaurant recommendations",
)
async def get_live_food_recommendations(
    city: str = Query(..., description="Destination city name (e.g. Udaipur, Goa, Manali)"),
    budget_tier: Optional[str] = Query("mid", description="budget, mid, luxury"),
):
    """
    Queries live DuckDuckGo and curated databases for famous local food spots,
    traditional thalis, iconic street food, and cafes with real INR pricing.
    """
    results = await LiveSearchService.get_food_recommendations(city=city, budget_tier=budget_tier)
    return APIResponse(
        success=True,
        data=results,
        message=f"Live food recommendations for {city} retrieved successfully",
    )


@router.get(
    "/live-stays",
    response_model=APIResponse[List[Dict[str, Any]]],
    status_code=status.HTTP_200_OK,
    summary="Live DuckDuckGo stay & hotel recommendations",
)
async def get_live_stay_recommendations(
    city: str = Query(..., description="Destination city name (e.g. Udaipur, Goa, Manali)"),
    budget_tier: Optional[str] = Query("mid", description="budget, mid, luxury"),
):
    """
    Queries live DuckDuckGo and curated databases for top-rated hotels, hostels (Zostel/Hosteller),
    homestays, and luxury heritage palace resorts with real INR pricing.
    """
    results = await LiveSearchService.get_stay_recommendations(city=city, budget_tier=budget_tier)
    return APIResponse(
        success=True,
        data=results,
        message=f"Live stay recommendations for {city} retrieved successfully",
    )
