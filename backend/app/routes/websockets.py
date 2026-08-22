import json
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from jose import JWTError, jwt
from sqlalchemy import select

from app.config import settings
from app.database import async_session_factory
from app.models.user import User
from app.models.trip import Trip
from app.models.trip_collaborator import TripCollaborator
from app.services.websocket_manager import ws_manager

logger = logging.getLogger("globetrotter.websockets")

router = APIRouter(prefix="/ws", tags=["Real-Time WebSockets & Collaboration"])


async def authenticate_ws_token(token: Optional[str]) -> Optional[User]:
    """Validates JWT token from WebSocket query parameter."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            return None

        async with async_session_factory() as session:
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    except JWTError:
        return None


@router.websocket("/trips/{trip_id}")
async def trip_collaboration_websocket(
    websocket: WebSocket,
    trip_id: str,
    token: Optional[str] = Query(None),
):
    """
    Live WebSocket channel for real-time trip collaboration.
    Handles presence updates, live change broadcasts, and editing indicators.
    """
    # 1. Authenticate user
    user = await authenticate_ws_token(token)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or missing authentication token")
        return

    # 2. Verify trip access permission
    async with async_session_factory() as session:
        trip_stmt = select(Trip).where(Trip.id == trip_id)
        trip_res = await session.execute(trip_stmt)
        trip = trip_res.scalar_one_or_none()

        if not trip:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Trip not found")
            return

        is_owner = (trip.user_id == user.id)
        if not is_owner:
            collab_stmt = select(TripCollaborator).where(
                TripCollaborator.trip_id == trip_id,
                TripCollaborator.user_id == user.id
            )
            collab_res = await session.execute(collab_stmt)
            collaborator = collab_res.scalar_one_or_none()
            if not collaborator and not trip.is_public:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Access denied to this trip")
                return

    user_info = {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "avatar_url": user.avatar_url,
    }

    # 3. Connect to room
    await ws_manager.connect_trip(trip_id=trip_id, websocket=websocket, user_info=user_info)

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                data = json.loads(raw_data)
            except Exception:
                data = {"type": "RAW_TEXT", "payload": raw_data}

            event_type = data.get("type", "MESSAGE")

            if event_type == "PING":
                await websocket.send_text(json.dumps({"type": "PONG"}))
            elif event_type in ["USER_FOCUS", "CHAT_MESSAGE", "TRIP_ACTION", "TYPING_STATUS"]:
                # Broadcast interaction to other collaborators in the room
                broadcast_payload = {
                    "type": event_type,
                    "user": user_info,
                    "data": data.get("data", {}),
                }
                await ws_manager.broadcast_to_trip(trip_id=trip_id, message=broadcast_payload, exclude=websocket)
            else:
                # Default broadcast
                await ws_manager.broadcast_to_trip(
                    trip_id=trip_id,
                    message={"type": event_type, "user": user_info, "data": data},
                    exclude=websocket
                )

    except WebSocketDisconnect:
        await ws_manager.disconnect_trip(trip_id=trip_id, websocket=websocket, user_id=user.id)
    except Exception as exc:
        logger.error(f"Trip WebSocket unexpected error: {str(exc)}")
        await ws_manager.disconnect_trip(trip_id=trip_id, websocket=websocket, user_id=user.id)


@router.websocket("/notifications")
async def user_notifications_websocket(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    """
    Live WebSocket channel for direct personal notifications (budget alerts, invites, etc.).
    """
    user = await authenticate_ws_token(token)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or missing authentication token")
        return

    await ws_manager.connect_user_notifications(user_id=user.id, websocket=websocket)

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                data = json.loads(raw_data)
                if data.get("type") == "PING":
                    await websocket.send_text(json.dumps({"type": "PONG"}))
            except Exception:
                pass
    except WebSocketDisconnect:
        await ws_manager.disconnect_user_notifications(user_id=user.id, websocket=websocket)
    except Exception as exc:
        logger.error(f"Notification WebSocket unexpected error: {str(exc)}")
        await ws_manager.disconnect_user_notifications(user_id=user.id, websocket=websocket)
