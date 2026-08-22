from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.user_controller import delete_account, get_profile, update_profile
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.user import UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=APIResponse[UserOut],
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Returns profile information of the currently authenticated traveler.
    """
    user = await get_profile(current_user=current_user)
    return APIResponse(
        success=True,
        data=user,
        message="User profile retrieved successfully",
    )


@router.put(
    "/me",
    response_model=APIResponse[UserOut],
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
)
async def update_my_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Updates the authenticated traveler's name, profile photo URL, or language.
    """
    updated_user = await update_profile(db=db, current_user=current_user, payload=payload)
    return APIResponse(
        success=True,
        data=updated_user,
        message="Profile updated successfully",
    )


@router.delete(
    "/me",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete user account",
)
async def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Permanently deletes the authenticated user account and all related trip records.
    """
    result = await delete_account(db=db, current_user=current_user)
    return APIResponse(
        success=True,
        data=result,
        message="Account deleted successfully",
    )
