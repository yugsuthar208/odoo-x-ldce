from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.controllers.trip_controller import get_trip_and_check_access
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.transit import TransitLeg, TransitOption
from app.schemas.common import APIResponse
from app.services.transit_service import TransitService
from pydantic import BaseModel

router = APIRouter(prefix="/trips", tags=["Transit & Routes"])

class SelectTransitOptionRequest(BaseModel):
    selected_option_id: str

@router.get(
    "/{trip_id}/transit",
    status_code=status.HTTP_200_OK,
    summary="Get Transit Legs and Options for a trip",
)
async def get_trip_transit(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetches the persisted authoritative transit legs and their generated options.
    """
    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="viewer")
    
    # Reload with explicit transit leg relationship
    result = await db.execute(
        select(TransitLeg)
        .options(selectinload(TransitLeg.options), selectinload(TransitLeg.selected_option))
        .where(TransitLeg.trip_id == trip_id)
        .order_by(TransitLeg.sequence.asc())
    )
    legs = result.scalars().all()
    
    # If no legs exist but trip has stops, we rebuild them
    if len(legs) == 0 and len(trip.stops) > 0:
        await TransitService.rebuild_transit_legs(db, trip)
        result = await db.execute(
            select(TransitLeg)
            .options(selectinload(TransitLeg.options), selectinload(TransitLeg.selected_option))
            .where(TransitLeg.trip_id == trip_id)
            .order_by(TransitLeg.sequence.asc())
        )
        legs = result.scalars().all()
        
    # Serialize for frontend
    serialized_legs = []
    for leg in legs:
        serialized_legs.append({
            "id": leg.id,
            "sequence": leg.sequence,
            "from_stop_id": leg.from_stop_id,
            "to_stop_id": leg.to_stop_id,
            "selected_option_id": leg.selected_option_id,
            "options": [
                {
                    "id": opt.id,
                    "mode": opt.mode,
                    "provider": opt.provider,
                    "duration_hours": opt.duration_hours,
                    "total_estimated_cost": opt.total_estimated_cost,
                    "cost_per_person": opt.cost_per_person,
                } for opt in leg.options
            ]
        })
        
    return APIResponse(
        success=True,
        data={
            "trip_id": trip.id,
            "journey_legs": serialized_legs,
        },
        message="Complete trip transit plan generated successfully",
    )


@router.patch(
    "/{trip_id}/transit/{leg_id}",
    status_code=status.HTTP_200_OK,
    summary="Select a transit option for a specific leg",
)
async def select_transit_option(
    trip_id: str,
    leg_id: str,
    payload: SelectTransitOptionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Selects a transit option for a leg and updates the authoritative backend state.
    """
    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="editor")
    
    leg = await db.get(TransitLeg, leg_id)
    if not leg or leg.trip_id != trip_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transit leg not found")
        
    option = await db.get(TransitOption, payload.selected_option_id)
    if not option or option.transit_leg_id != leg.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid option for this leg")
        
    leg.selected_option_id = option.id
    leg.selected_option = option
    db.add(leg)
    await db.flush()
    await db.commit()
    
    # Recalculate and fetch budget
    from app.services.budget_service import BudgetService
    updated_budget = await BudgetService.calculate_authoritative_budget(db, trip_id)
    
    return APIResponse(
        success=True,
        data={
            "leg_id": leg.id,
            "selected_option_id": option.id,
            "mode": option.mode,
            "provider": option.provider,
            "budget": updated_budget
        },
        message="Transit option selected successfully. Budget recalculated."
    )
