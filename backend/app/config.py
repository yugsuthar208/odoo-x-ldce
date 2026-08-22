import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables and .env file."""

    PROJECT_NAME: str = "GlobeTrotter"
    API_V1_STR: str = "/api"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: list[str] | str = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Database configuration (Defaults to PostgreSQL asyncpg, falls back to SQLite for local tests)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./globetrotter.db"
    )
    
    # JWT Authentication configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_jwt_key_globetrotter_2026_change_in_prod")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_DAYS: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "7"))
    
    # Budget configuration constants (in INR)
    MEALS_PER_DAY_INR: float = float(os.getenv("MEALS_PER_DAY_INR", "800.0"))
    MEALS_PER_DAY_USD: float = float(os.getenv("MEALS_PER_DAY_USD", "800.0"))
    DEFAULT_CITY_COST_INDEX: float = float(os.getenv("DEFAULT_CITY_COST_INDEX", "55.0"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Supabase Configuration
    SUPABASE_PROJECT_ID: str = os.getenv("SUPABASE_PROJECT_ID", "aoosujaabsdmnzqothhw")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://aoosujaabsdmnzqothhw.supabase.co")
    SUPABASE_PUBLISHABLE_KEY: str = os.getenv("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_ZbzM4M2DfhEvUuXA_0AvaQ_j9BlM-eL")
    SUPABASE_SECRET_KEY: str = os.getenv("SUPABASE_SECRET_KEY", "sb_secret_DOnkU3w3X-TKgLjBs6DV5A_r84cT7Aq")

    # ML Model storage path
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    ML_MODEL_PATH: Path = BASE_DIR / "app" / "ml" / "budget_model.pkl"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
