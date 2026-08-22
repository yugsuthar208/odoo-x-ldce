from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserUpdate


async def get_profile(current_user: User) -> User:
    """Returns the authenticated traveler's profile."""
    return current_user


async def update_profile(db: AsyncSession, current_user: User, payload: UserUpdate) -> User:
    """Updates the user profile fields (name, profile_photo, language)."""
    if payload.name is not None:
        current_user.name = payload.name.strip()
    if payload.profile_photo is not None:
        current_user.profile_photo = payload.profile_photo
    if payload.language is not None:
        current_user.language = payload.language

    db.add(current_user)
    await db.flush()
    await db.refresh(current_user)
    return current_user


async def delete_account(db: AsyncSession, current_user: User) -> dict:
    """Deletes the authenticated user account and all associated trip data."""
    await db.delete(current_user)
    await db.flush()
    return {"message": "Account deleted successfully"}
