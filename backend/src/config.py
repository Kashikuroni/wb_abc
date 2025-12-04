from pathlib import Path
from datetime import timedelta
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from authx import AuthXConfig

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    SECRET: str
    JWT_SECRET_KEY: str

    BASE_DIR: Path = BASE_DIR
    STATIC_DIR: Path = STATIC_DIR

    model_config = SettingsConfigDict(extra="ignore")


class RadisCacheSettings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_TTL: int = 3600 * 24

    model_config = SettingsConfigDict(extra="ignore")


class WbSettings(BaseSettings):
    API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(extra="ignore")


settings = Settings()  # pyright: ignore


authx_config = AuthXConfig(
    JWT_SECRET_KEY=settings.JWT_SECRET_KEY,
    JWT_ALGORITHM="HS256",
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=30),
    JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=15),
    JWT_TOKEN_LOCATION=["cookies"],
    JWT_COOKIE_SECURE=True,
    JWT_COOKIE_SAMESITE="lax",
    JWT_COOKIE_CSRF_PROTECT=False,
    JWT_ACCESS_COOKIE_NAME="access_token",
    JWT_REFRESH_COOKIE_NAME="refresh_token",
)


def get_db_url() -> str:
    return (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
