from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.trip import Trip
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogResponse
from app.middleware.rbac import require_trip_role

router = APIRouter(prefix="/trips", tags=["Security & Audit Logs"])


@router.get(
    "/{trip_id}/audit-logs",
    response_model=List[AuditLogResponse],
    summary="Get Trip Audit Trail",
    description="Returns immutable audit events for a trip. Requires 'editor' or 'owner' role."
)
async def get_trip_audit_logs(
    trip_id: str,
    limit: int = Query(50, ge=1, le=200),
    auth_context: tuple[User, Trip, str] = Depends(require_trip_role("editor")),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetches the history of actions, modifications, and permission changes on this trip.
    """
    user, trip, role = auth_context

    stmt = (
        select(AuditLog)
        .where(AuditLog.trip_id == trip_id)
        .order_by(desc(AuditLog.created_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()

    return [AuditLogResponse.model_validate(log) for log in logs]
