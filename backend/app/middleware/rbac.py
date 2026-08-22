from typing import Literal, Optional
from fastapi import Depends, HTTPException, status, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.trip import Trip
from app.models.trip_collaborator import TripCollaborator
from app.middleware.auth import get_current_user

# Role hierarchy ranking
ROLE_LEVELS = {
    "viewer": 1,
    "editor": 2,
    "owner": 3,
}

TripRole = Literal["viewer", "editor", "owner"]


def require_trip_role(min_role: TripRole = "viewer"):
    """
    FastAPI dependency factory enforcing Role-Based Access Control (RBAC) on trip resources.
    
    Validates that:
    1. The trip exists.
    2. The current user is either:
       - The Trip Owner (`trip.user_id == current_user.id` -> implicit 'owner' role).
       - Or has an active `TripCollaborator` record with rank >= `min_role`.
    
    Returns a tuple of (User, Trip, effective_role: str).
    """
    async def role_checker(
        trip_id: str = Path(..., description="Target Trip UUID"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> tuple[User, Trip, str]:
        # 1. Fetch trip
        stmt = select(Trip).where(Trip.id == trip_id)
        result = await db.execute(stmt)
        trip = result.scalar_one_or_none()

        if trip is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )

        # 2. Check if owner
        if trip.user_id == current_user.id:
            return current_user, trip, "owner"

        # 3. Check collaborator role
        collab_stmt = select(TripCollaborator).where(
            TripCollaborator.trip_id == trip_id,
            TripCollaborator.user_id == current_user.id
        )
        collab_result = await db.execute(collab_stmt)
        collaborator = collab_result.scalar_one_or_none()

        if collaborator is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You are not a member of this trip"
            )

        user_role = collaborator.role.lower()
        user_rank = ROLE_LEVELS.get(user_role, 0)
        required_rank = ROLE_LEVELS.get(min_role.lower(), 1)

        if user_rank < required_rank:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Requires '{min_role}' role (Current: '{user_role}')"
            )

        return current_user, trip, user_role

    return role_checker
