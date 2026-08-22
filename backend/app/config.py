import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables and .env file."""

    PROJECT_NAME: str = "GlobeTrotter"
    API_V1_STR: str = "/api"
    
    # Database configuration (Defaults to PostgreSQL asyncpg, falls back to SQLite for local tests)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./globetrotter.db"
    )
    
    # JWT Authentication configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_jwt_key_globetrotter_2026_change_in_prod")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_DAYS: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "7"))
    
    # Budget configuration constants
    MEALS_PER_DAY_USD: float = float(os.getenv("MEALS_PER_DAY_USD", "25.0"))
    
    # ML Model storage path
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    ML_MODEL_PATH: Path = BASE_DIR / "app" / "ml" / "budget_model.pkl"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
