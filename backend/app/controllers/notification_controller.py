import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.notification import Notification
from app.schemas.notification import NotificationResponse
from app.services.websocket_manager import ws_manager

logger = logging.getLogger("globetrotter.notifications")


class NotificationController:
    """Controller handling in-app notifications creation, retrieval, and updates."""

    @staticmethod
    async def create_and_push(
        db: AsyncSession,
        user_id: str,
        type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        """
        Saves a notification to the database and dispatches it over WebSocket in real time.
        """
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            data=data or {},
            is_read=False,
        )
        db.add(notification)
        await db.commit()
        await db.refresh(notification)

        # Dispatch real-time alert via WebSocket
        try:
            await ws_manager.send_notification_to_user(
                user_id=user_id,
                notification_data=NotificationResponse.model_validate(notification).model_dump(mode="json"),
            )
        except Exception as exc:
            logger.warning(f"Failed to push real-time notification to user {user_id}: {str(exc)}")

        return notification

    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
    ) -> List[Notification]:
        """Fetches notifications for a specific user."""
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read == False)
        stmt = stmt.order_by(desc(Notification.created_at)).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def mark_as_read(db: AsyncSession, notification_id: str, user_id: str) -> Notification:
        """Marks a notification as read."""
        stmt = select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
        result = await db.execute(stmt)
        notification = result.scalar_one_or_none()

        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

        notification.is_read = True
        await db.commit()
        await db.refresh(notification)
        return notification

    @staticmethod
    async def mark_all_as_read(db: AsyncSession, user_id: str) -> int:
        """Marks all unread notifications for a user as read."""
        stmt = select(Notification).where(Notification.user_id == user_id, Notification.is_read == False)
        result = await db.execute(stmt)
        notifications = result.scalars().all()

        for notif in notifications:
            notif.is_read = True

        await db.commit()
        return len(notifications)
