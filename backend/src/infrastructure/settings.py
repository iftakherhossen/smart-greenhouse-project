from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    postgres_user: str = "greenhouse"
    postgres_password: str = "greenhouse"
    postgres_db: str = "greenhouse"
    postgres_host: str = "localhost"
    postgres_port: int = 5433

    database_url: str = (
        "postgresql+psycopg://"
        "greenhouse:greenhouse@localhost:5433/greenhouse"
    )

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()