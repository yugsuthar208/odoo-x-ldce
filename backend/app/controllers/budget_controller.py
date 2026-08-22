from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.trip_controller import calculate_trip_budget, get_trip_and_check_access
from app.models.budget import Budget
from app.models.user import User
from app.schemas.budget import BudgetUpdate


async def update_trip_budget_settings(
    db: AsyncSession,
    trip_id: str,
    current_user: User,
    payload: BudgetUpdate,
) -> dict:
    """Updates manual budget fields and returns recalculated budget forecast."""
    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="editor")

    if trip.budget is None:
        trip.budget = Budget(trip_id=trip.id)
        db.add(trip.budget)

    if payload.transport_cost is not None:
        trip.budget.transport_cost = payload.transport_cost
    if payload.misc_cost is not None:
        trip.budget.misc_cost = payload.misc_cost
    if payload.total_budget_limit is not None:
        trip.budget.total_budget_limit = payload.total_budget_limit
        trip.total_budget = payload.total_budget
        trip.budget_target = payload.total_budget_limit # Save user intent to the new authoritative column
        db.add(trip)

    db.add(trip.budget)
    await db.flush()

    return await calculate_trip_budget(trip_id=trip_id, current_user=current_user, db=db)
