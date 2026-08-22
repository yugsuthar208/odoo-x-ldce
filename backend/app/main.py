from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.ml.budget_predictor import BudgetPredictor
from app.ml.recommender import HybridRecommender
from app.middleware.observability import ObservabilityMiddleware
from app.routes import (
    activities_router,
    auth_router,
    cities_router,
    expenses_router,
    favorites_router,
    itinerary_router,
    recommend_router,
    shared_router,
    stops_router,
    trips_router,
    users_router,
    notifications_router,
    websockets_router,
    metrics_router,
    audit_router,
    oauth_router,
    places_router,
    transit_router,
)

logger = logging.getLogger("GlobeTrotterAPI")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events:
    - Automatically creates/synchronizes all database tables.
    - Preloads Scikit-Learn / XGBoost and SentenceTransformer models into app.state.
    - Logs startup and teardown messages.
    """
    print("[GlobeTrotter API] Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("[GlobeTrotter API] Initializing upgraded ML modules...")
    app.state.budget_predictor = BudgetPredictor()
    if not app.state.budget_predictor.load():
        logger.warning("ML BudgetPredictor not found. Run python app/ml/train.py first.")

    app.state.recommender = HybridRecommender()
    if not app.state.recommender.load():
        logger.warning("ML HybridRecommender not found. Run python app/ml/train.py first.")

    print("GlobeTrotter API started")

    yield

    await engine.dispose()
    print("[GlobeTrotter API] Database connections closed.")


# FastAPI Application Instance
app = FastAPI(
    title="GlobeTrotter API",
    version="1.0.0",
    description="Personalized Travel Planning Platform with Machine Learning & AI Intelligence",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Observability & Correlation ID Middleware
app.add_middleware(ObservabilityMiddleware)

# CORS Middleware
origins = settings.BACKEND_CORS_ORIGINS
if isinstance(origins, str):
    origins = [item.strip() for item in origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# EXCEPTION HANDLERS (Standardized Error Response Format)
# Format: { "success": false, "error": "...", "status_code": 4xx/5xx }
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handles standard HTTP exceptions with unified error structure."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles Pydantic request validation errors."""
    error_messages = []
    for err in exc.errors():
        loc = " -> ".join([str(l) for l in err.get("loc", [])])
        msg = err.get("msg", "Validation error")
        error_messages.append(f"{loc}: {msg}")

    error_summary = "; ".join(error_messages) if error_messages else "Request validation failed"
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": error_summary,
            "status_code": 400,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catches unhandled internal server exceptions."""
    print(f"[GlobeTrotter API ERROR] Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "An internal server error occurred",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
    )


# ============================================================================
# HEALTH & METRICS ENDPOINTS
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Service health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}

app.include_router(metrics_router)  # /metrics root endpoint


# ============================================================================
# ROUTE REGISTRATIONS
# ============================================================================

api_v1_prefix = settings.API_V1_STR

app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(oauth_router, prefix=api_v1_prefix)
app.include_router(users_router, prefix=api_v1_prefix)
app.include_router(cities_router, prefix=api_v1_prefix)
app.include_router(activities_router, prefix=api_v1_prefix)
app.include_router(trips_router, prefix=api_v1_prefix)
app.include_router(stops_router, prefix=api_v1_prefix)
app.include_router(itinerary_router, prefix=api_v1_prefix)
app.include_router(expenses_router, prefix=api_v1_prefix)
app.include_router(shared_router, prefix=api_v1_prefix)
app.include_router(favorites_router, prefix=api_v1_prefix)
app.include_router(recommend_router, prefix=api_v1_prefix)
app.include_router(notifications_router, prefix=api_v1_prefix)
app.include_router(websockets_router, prefix=api_v1_prefix)
app.include_router(audit_router, prefix=api_v1_prefix)
app.include_router(places_router, prefix=api_v1_prefix)
app.include_router(transit_router, prefix=api_v1_prefix)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
