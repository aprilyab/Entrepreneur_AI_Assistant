# backend/app/config.py
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    app_name: str = "Prooflane"
    app_version: str = "0.2.0"
    debug: bool = False

    # LLM
    gemini_api_key: str = ""
    gemini_api_keys: list[str] = Field(default_factory=list)
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_rotation_enabled: bool = True

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/entrepreneur_ai"
    database_url_async: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/entrepreneur_ai"

    # Auth
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

@lru_cache()
def get_settings() -> Settings:
    return Settings()
