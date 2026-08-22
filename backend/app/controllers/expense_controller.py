from typing import List
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.controllers.trip_controller import get_trip_and_check_access
from app.models.expense import Expense
from app.models.trip import Trip
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.services.audit_service import log_audit_event
from app.controllers.notification_controller import NotificationController
from app.services.websocket_manager import ws_manager


async def create_expense(
    db: AsyncSession,
    trip_id: str,
    current_user: User,
    payload: ExpenseCreate,
) -> Expense:
    """Logs an expense for a trip after verifying editor/owner access."""
    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="editor")

    expense = Expense(
        trip_id=trip_id,
        category=payload.category,
        description=payload.description.strip(),
        estimated_amount=payload.estimated_amount,
        actual_amount=payload.actual_amount,
        currency=payload.currency or "USD",
        paid_by=payload.paid_by or current_user.id,
    )
    db.add(expense)
    await db.flush()
    await db.refresh(expense)

    # Log audit event
    await log_audit_event(
        db=db,
        action="EXPENSE_CREATED",
        resource_type="expense",
        resource_id=expense.id,
        user_id=current_user.id,
        trip_id=trip_id,
        details={
            "description": expense.description,
            "actual_amount": expense.actual_amount,
            "category": expense.category,
        },
    )

    # Broadcast expense creation to live trip room
    await ws_manager.broadcast_to_trip(
        trip_id=trip_id,
        message={
            "type": "EXPENSE_EVENT",
            "action": "EXPENSE_CREATED",
            "expense": {
                "id": expense.id,
                "description": expense.description,
                "amount": expense.actual_amount or expense.estimated_amount,
                "category": expense.category,
            }
        }
    )

    # Check budget threshold for budget alert notification
    if trip.total_budget and trip.total_budget > 0:
        # Sum actual expenses
        exp_res = await db.execute(select(Expense).where(Expense.trip_id == trip_id))
        all_exp = exp_res.scalars().all()
        total_spent = sum((e.actual_amount or e.estimated_amount or 0.0) for e in all_exp)
        usage_pct = (total_spent / trip.total_budget) * 100

        if usage_pct >= 90.0:
            await NotificationController.create_and_push(
                db=db,
                user_id=trip.user_id,
                type="BUDGET_ALERT",
                title=f"⚠️ Budget Warning: {trip.title}",
                message=f"You have used {usage_pct:.1f}% of your budget for '{trip.title}' (${total_spent:.2f}/${trip.total_budget:.2f}).",
                data={"trip_id": trip_id, "usage_pct": round(usage_pct, 1), "total_spent": total_spent},
            )

    return expense


async def list_trip_expenses(
    db: AsyncSession,
    trip_id: str,
    current_user: User,
) -> List[Expense]:
    """Lists all expenses for a trip."""
    await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="viewer")

    res = await db.execute(
        select(Expense)
        .options(selectinload(Expense.paid_by_user))
        .where(Expense.trip_id == trip_id)
        .order_by(Expense.created_at.desc())
    )
    return list(res.scalars().all())


async def update_expense(
    db: AsyncSession,
    expense_id: str,
    current_user: User,
    payload: ExpenseUpdate,
) -> Expense:
    """Modifies an expense entry."""
    res = await db.execute(
        select(Expense).options(selectinload(Expense.trip)).where(Expense.id == expense_id)
    )
    expense = res.scalar_one_or_none()

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id '{expense_id}' not found",
        )

    await get_trip_and_check_access(db=db, trip_id=expense.trip_id, user_id=current_user.id, required_role="editor")

    if payload.category is not None:
        expense.category = payload.category
    if payload.description is not None:
        expense.description = payload.description.strip()
    if payload.estimated_amount is not None:
        expense.estimated_amount = payload.estimated_amount
    if payload.actual_amount is not None:
        expense.actual_amount = payload.actual_amount
    if payload.currency is not None:
        expense.currency = payload.currency
    if payload.paid_by is not None:
        expense.paid_by = payload.paid_by

    db.add(expense)
    await db.flush()
    await db.refresh(expense)
    return expense


async def delete_expense(
    db: AsyncSession,
    expense_id: str,
    current_user: User,
) -> dict:
    """Deletes an expense entry."""
    expense = await db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id '{expense_id}' not found",
        )

    await get_trip_and_check_access(db=db, trip_id=expense.trip_id, user_id=current_user.id, required_role="editor")

    await db.delete(expense)
    await db.flush()
    return {"message": "Expense deleted successfully"}
