from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.expense_controller import delete_expense, update_expense
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.expense import ExpenseOut, ExpenseUpdate

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.put(
    "/{id}",
    response_model=APIResponse[ExpenseOut],
    status_code=status.HTTP_200_OK,
    summary="Update an expense entry",
)
async def edit_expense(
    id: str,
    payload: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Modifies an existing expense record."""
    expense = await update_expense(db=db, expense_id=id, current_user=current_user, payload=payload)
    return APIResponse(
        success=True,
        data=expense,
        message="Expense updated successfully",
    )


@router.delete(
    "/{id}",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete an expense entry",
)
async def remove_expense(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deletes an expense record from a trip."""
    result = await delete_expense(db=db, expense_id=id, current_user=current_user)
    return APIResponse(
        success=True,
        data=result,
        message="Expense deleted successfully",
    )
