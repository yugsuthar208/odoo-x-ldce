import json
import logging
from typing import Dict, Set, Any, Optional
from fastapi import WebSocket
from app.services.metrics import ACTIVE_WEBSOCKETS

logger = logging.getLogger("globetrotter.websockets")


class ConnectionManager:
    """
    Manages live WebSocket connections for:
    1. Trip collaboration rooms (presence, live updates, focus indicators).
    2. User-specific notification streams.
    """
    def __init__(self):
        # trip_id -> Set of WebSockets
        self.trip_rooms: Dict[str, Set[WebSocket]] = {}
        # trip_id -> Dict of user_id -> user metadata
        self.trip_presence: Dict[str, Dict[str, Dict[str, Any]]] = {}
        # user_id -> Set of WebSockets (for cross-device notifications)
        self.user_streams: Dict[str, Set[WebSocket]] = {}

    async def connect_trip(self, trip_id: str, websocket: WebSocket, user_info: Dict[str, Any]):
        """Registers a collaborator into a trip room."""
        await websocket.accept()
        if trip_id not in self.trip_rooms:
            self.trip_rooms[trip_id] = set()
            self.trip_presence[trip_id] = {}

        self.trip_rooms[trip_id].add(websocket)
        user_id = user_info.get("id")
        if user_id:
            self.trip_presence[trip_id][user_id] = user_info

        ACTIVE_WEBSOCKETS.labels(channel="trip_rooms").inc()
        logger.info(f"WebSocket client connected to trip room {trip_id} (User: {user_id})")

        # Broadcast active presence list to all participants in this trip
        await self.broadcast_to_trip(
            trip_id=trip_id,
            message={
                "type": "PRESENCE_UPDATE",
                "active_users": list(self.trip_presence[trip_id].values()),
                "event": "USER_JOINED",
                "user": user_info,
            }
        )

    async def disconnect_trip(self, trip_id: str, websocket: WebSocket, user_id: Optional[str] = None):
        """Removes a collaborator from a trip room and broadcasts departure."""
        if trip_id in self.trip_rooms and websocket in self.trip_rooms[trip_id]:
            self.trip_rooms[trip_id].remove(websocket)
            ACTIVE_WEBSOCKETS.labels(channel="trip_rooms").dec()

            if user_id and trip_id in self.trip_presence:
                departed_user = self.trip_presence[trip_id].pop(user_id, None)
                if not self.trip_rooms[trip_id]:
                    del self.trip_rooms[trip_id]
                    del self.trip_presence[trip_id]
                else:
                    await self.broadcast_to_trip(
                        trip_id=trip_id,
                        message={
                            "type": "PRESENCE_UPDATE",
                            "active_users": list(self.trip_presence[trip_id].values()),
                            "event": "USER_LEFT",
                            "user": departed_user,
                        }
                    )
            logger.info(f"WebSocket client disconnected from trip room {trip_id}")

    async def broadcast_to_trip(self, trip_id: str, message: Dict[str, Any], exclude: Optional[WebSocket] = None):
        """Sends a JSON payload to all active clients in a trip room."""
        if trip_id not in self.trip_rooms:
            return

        dead_sockets = set()
        payload = json.dumps(message)

        for ws in self.trip_rooms[trip_id]:
            if ws != exclude:
                try:
                    await ws.send_text(payload)
                except Exception as exc:
                    logger.warning(f"Error sending message to client in trip {trip_id}: {str(exc)}")
                    dead_sockets.add(ws)

        for dead_ws in dead_sockets:
            self.trip_rooms[trip_id].discard(dead_ws)

    # -------------------------------------------------------------------------
    # User Notification Stream Management
    # -------------------------------------------------------------------------
    async def connect_user_notifications(self, user_id: str, websocket: WebSocket):
        """Registers a user socket to receive personal in-app alerts."""
        await websocket.accept()
        if user_id not in self.user_streams:
            self.user_streams[user_id] = set()

        self.user_streams[user_id].add(websocket)
        ACTIVE_WEBSOCKETS.labels(channel="user_notifications").inc()
        logger.info(f"Notification WebSocket connected for user {user_id}")

    async def disconnect_user_notifications(self, user_id: str, websocket: WebSocket):
        """Removes a user socket from notification stream."""
        if user_id in self.user_streams and websocket in self.user_streams[user_id]:
            self.user_streams[user_id].remove(websocket)
            ACTIVE_WEBSOCKETS.labels(channel="user_notifications").dec()
            if not self.user_streams[user_id]:
                del self.user_streams[user_id]
            logger.info(f"Notification WebSocket disconnected for user {user_id}")

    async def send_notification_to_user(self, user_id: str, notification_data: Dict[str, Any]):
        """Pushes a notification frame to all active connections of a user."""
        if user_id not in self.user_streams:
            return

        dead_sockets = set()
        payload = json.dumps({"type": "NEW_NOTIFICATION", "notification": notification_data})

        for ws in self.user_streams[user_id]:
            try:
                await ws.send_text(payload)
            except Exception:
                dead_sockets.add(ws)

        for dead_ws in dead_sockets:
            self.user_streams[user_id].discard(dead_ws)


# Global singleton instance
ws_manager = ConnectionManager()
