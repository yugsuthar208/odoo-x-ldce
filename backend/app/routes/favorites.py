from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.favorite_controller import (
    add_favorite,
    delete_favorite,
    list_favorites,
)
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.favorite import FavoriteCreate, FavoriteOut

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.post(
    "",
    response_model=APIResponse[FavoriteOut],
    status_code=status.HTTP_201_CREATED,
    summary="Bookmark a destination city or activity",
)
async def bookmark_item(
    payload: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Saves a city or activity to the traveler's favorites list."""
    fav = await add_favorite(db=db, user_id=current_user.id, payload=payload)
    return APIResponse(
        success=True,
        data=fav,
        message="Item added to favorites successfully",
    )


@router.get(
    "",
    response_model=APIResponse[List[FavoriteOut]],
    status_code=status.HTTP_200_OK,
    summary="List all bookmarks for current user",
)
async def get_my_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves all bookmarked cities and activities for the traveler."""
    favs = await list_favorites(db=db, user_id=current_user.id)
    return APIResponse(
        success=True,
        data=favs,
        message="Favorites retrieved successfully",
    )


@router.delete(
    "/{id}",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Remove a bookmark",
)
async def remove_my_favorite(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Removes an item from favorites."""
    result = await delete_favorite(db=db, favorite_id=id, user_id=current_user.id)
    return APIResponse(
        success=True,
        data=result,
        message="Favorite removed successfully",
    )
