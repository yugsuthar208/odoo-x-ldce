from app.routes.activities import router as activities_router
from app.routes.auth import router as auth_router
from app.routes.cities import router as cities_router
from app.routes.recommend import router as recommend_router
from app.routes.stops import router as stops_router
from app.routes.trips import router as trips_router
from app.routes.users import router as users_router

__all__ = [
    "auth_router",
    "users_router",
    "cities_router",
    "trips_router",
    "stops_router",
    "activities_router",
    "recommend_router",
]
