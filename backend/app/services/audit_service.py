import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from app.services.metrics import AUDIT_EVENTS_TOTAL

logger = logging.getLogger("globetrotter.audit")


async def log_audit_event(
    db: AsyncSession,
    action: str,
    resource_type: str,
    user_id: Optional[str] = None,
    trip_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """
    Persists an immutable audit log entry into the database and increments Prometheus metrics.
    """
    try:
        audit_entry = AuditLog(
            user_id=user_id,
            trip_id=trip_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
        )
        db.add(audit_entry)
        await db.commit()
        await db.refresh(audit_entry)
        
        AUDIT_EVENTS_TOTAL.labels(action=action).inc()
        logger.info(f"Audit event logged: [{action}] on {resource_type}:{resource_id} by user {user_id}")
        return audit_entry
    except Exception as exc:
        logger.error(f"Failed to record audit event [{action}]: {str(exc)}", exc_info=True)
        # Avoid crashing the caller transaction if audit logging encounters a transient DB issue
        return None
