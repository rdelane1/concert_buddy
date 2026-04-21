"""Application configuration - environment variables and settings."""

from functools import lru_cache
from os import getenv
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_env_file() -> Path:
    """Resolve the environment file path independent of current working directory."""
    project_root = Path(__file__).resolve().parents[3]
    env_file_override = getenv("APP_ENV_FILE")

    if not env_file_override:
        return project_root / ".env"

    env_path = Path(env_file_override).expanduser()
    if env_path.is_absolute():
        return env_path

    return (project_root / env_path).resolve()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Load from .env file
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="allow",
    )

    # FastAPI settings
    title: str = "Concert Buddy API"
    version: str = "1.0.0"
    allow_origins: list[str] = ["http://localhost:3000"]  # CORS allowed origins

    # Uvicorn settings
    uvicorn_host: str = "localhost"
    uvicorn_port: int = 8000

    # Agent settings
    manager_model: str = "gpt-5"
    manager_reasoning_effort: str = "low"
    manager_verbosity: str = "low"

    concert_agent_model: str = "gpt-5"
    concert_agent_reasoning_effort: str = "low"
    concert_agent_verbosity: str = "low"

    ticket_agent_model: str = "gpt-5"
    ticket_agent_reasoning_effort: str = "low"
    ticket_agent_verbosity: str = "low"

    playlist_agent_model: str = "gpt-5"
    playlist_agent_reasoning_effort: str = "low"
    playlist_agent_verbosity: str = "low"


# Cache settings instance to avoid reloading environment variables multiple times
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings loaded from environment variables."""
    return Settings(_env_file=_resolve_env_file(), _env_file_encoding="utf-8")
