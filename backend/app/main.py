from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.ml.budget_predictor import get_or_load_model
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
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events:
    - Automatically creates/synchronizes all database tables.
    - Preloads Scikit-Learn machine learning budget model.
    - Logs startup and teardown messages.
    """
    print("[GlobeTrotter API] Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("[GlobeTrotter API] Initializing ML models...")
    get_or_load_model()
    print("GlobeTrotter API started")

    yield

    await engine.dispose()
    print("[GlobeTrotter API] Database connections closed.")


# FastAPI Application Instance
app = FastAPI(
    title="GlobeTrotter API",
    version="1.0.0",
    description="Personalized Travel Planning Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware (Allows all origins for frontend development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
# HEALTH CHECK
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Service health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}


# ============================================================================
# ROUTE REGISTRATIONS
# ============================================================================

api_v1_prefix = settings.API_V1_STR

app.include_router(auth_router, prefix=api_v1_prefix)
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
