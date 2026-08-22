from typing import List
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.controllers.trip_controller import get_trip_and_check_access
from app.models.trip_collaborator import TripCollaborator
from app.models.user import User
from app.schemas.trip_collaborator import CollaboratorAddRequest


async def add_collaborator(
    db: AsyncSession,
    trip_id: str,
    current_user: User,
    payload: CollaboratorAddRequest,
) -> TripCollaborator:
    """Adds a collaborator to a trip (owner only)."""
    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="owner")

    user_res = await db.execute(select(User).where(User.email == payload.email.lower().strip()))
    target_user = user_res.scalar_one_or_none()

    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{payload.email}' not found",
        )

    if target_user.id == trip.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The trip owner cannot be added as a collaborator",
        )

    # Check if already a collaborator
    existing = await db.execute(
        select(TripCollaborator).where(
            TripCollaborator.trip_id == trip_id,
            TripCollaborator.user_id == target_user.id,
        )
    )
    collab = existing.scalar_one_or_none()

    role_val = payload.role.lower() if payload.role.lower() in ["editor", "viewer"] else "editor"

    if collab:
        collab.role = role_val
    else:
        collab = TripCollaborator(
            trip_id=trip_id,
            user_id=target_user.id,
            role=role_val,
        )
        db.add(collab)

    await db.flush()

    res = await db.execute(
        select(TripCollaborator)
        .options(selectinload(TripCollaborator.user))
        .where(TripCollaborator.id == collab.id)
    )
    return res.scalar_one()


async def list_collaborators(
    db: AsyncSession,
    trip_id: str,
    current_user: User,
) -> List[TripCollaborator]:
    """Lists collaborators for a trip."""
    await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="viewer")

    res = await db.execute(
        select(TripCollaborator)
        .options(selectinload(TripCollaborator.user))
        .where(TripCollaborator.trip_id == trip_id)
        .order_by(TripCollaborator.joined_at.asc())
    )
    return list(res.scalars().all())


async def remove_collaborator(
    db: AsyncSession,
    trip_id: str,
    user_id_to_remove: str,
    current_user: User,
) -> dict:
    """Removes a collaborator from a trip (owner only or self removal)."""
    trip = await get_trip_and_check_access(db=db, trip_id=trip_id, user_id=current_user.id, required_role="viewer")

    if current_user.id != trip.user_id and current_user.id != user_id_to_remove:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the trip owner or the collaborator themselves can remove this collaborator",
        )

    res = await db.execute(
        select(TripCollaborator).where(
            TripCollaborator.trip_id == trip_id,
            TripCollaborator.user_id == user_id_to_remove,
        )
    )
    collab = res.scalar_one_or_none()

    if collab is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaborator not found on this trip",
        )

    await db.delete(collab)
    await db.flush()
    return {"message": "Collaborator removed successfully"}
