from typing import List
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity import Activity
from app.models.city import City
from app.models.favorite import Favorite
from app.schemas.favorite import FavoriteCreate


async def add_favorite(
    db: AsyncSession,
    user_id: str,
    payload: FavoriteCreate,
) -> Favorite:
    """Bookmarks a city or activity for the authenticated traveler."""
    if payload.city_id:
        city = await db.get(City, payload.city_id)
        if city is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
    if payload.activity_id:
        act = await db.get(Activity, payload.activity_id)
        if act is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    # Check for existing duplicate
    q = select(Favorite).where(
        Favorite.user_id == user_id,
        Favorite.city_id == payload.city_id,
        Favorite.activity_id == payload.activity_id,
    )
    existing = (await db.execute(q)).scalar_one_or_none()
    if existing:
        return existing

    favorite = Favorite(
        user_id=user_id,
        city_id=payload.city_id,
        activity_id=payload.activity_id,
    )
    db.add(favorite)
    await db.flush()

    res = await db.execute(
        select(Favorite)
        .options(selectinload(Favorite.city), selectinload(Favorite.activity))
        .where(Favorite.id == favorite.id)
    )
    return res.scalar_one()


async def list_favorites(db: AsyncSession, user_id: str) -> List[Favorite]:
    """Returns all bookmarked items for the user."""
    res = await db.execute(
        select(Favorite)
        .options(selectinload(Favorite.city), selectinload(Favorite.activity))
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
    )
    return list(res.scalars().all())


async def delete_favorite(db: AsyncSession, favorite_id: str, user_id: str) -> dict:
    """Removes a bookmark."""
    fav = await db.get(Favorite, favorite_id)
    if fav is None or fav.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite entry not found")

    await db.delete(fav)
    await db.flush()
    return {"message": "Favorite removed successfully"}
