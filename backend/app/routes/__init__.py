from app.routes.activities import router as activities_router
from app.routes.auth import router as auth_router
from app.routes.cities import router as cities_router
from app.routes.expenses import router as expenses_router
from app.routes.favorites import router as favorites_router
from app.routes.itinerary import router as itinerary_router
from app.routes.recommend import router as recommend_router
from app.routes.shared import router as shared_router
from app.routes.stops import router as stops_router
from app.routes.trips import router as trips_router
from app.routes.users import router as users_router
from app.routes.notifications import router as notifications_router
from app.routes.websockets import router as websockets_router
from app.routes.metrics import router as metrics_router
from app.routes.audit import router as audit_router
from app.routes.oauth import router as oauth_router
from app.routes.places import router as places_router
from app.routes.transit import router as transit_router
from app.routes.ai_planner import router as ai_planner_router

__all__ = [
    "auth_router",
    "users_router",
    "cities_router",
    "trips_router",
    "stops_router",
    "activities_router",
    "itinerary_router",
    "expenses_router",
    "shared_router",
    "favorites_router",
    "recommend_router",
    "notifications_router",
    "websockets_router",
    "metrics_router",
    "audit_router",
    "oauth_router",
    "places_router",
    "transit_router",
    "ai_planner_router",
]
