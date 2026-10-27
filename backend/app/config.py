"""
Application Configuration — Pydantic Settings
All values are loaded from environment variables or the repo-root .env file.
"""
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = REPO_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────
    APP_NAME: str = "Metago AI Marketing Platform"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    OPERATING_MODE: Literal["demo", "assisted", "controlled"] = "demo"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "CHANGE_ME_in_production"
    ENCRYPTION_KEY: str = "CHANGE_ME_generate_with_fernet"

    # ── Database ───────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./metago.db"
    SYNC_DATABASE_URL: str = "sqlite:///./metago.db"

    # ── Redis ──────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── JWT ────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "CHANGE_ME_jwt_secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── LLM ───────────────────────────────────────────────────────
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    DEFAULT_LLM_MODEL: str = "anthropic/claude-3-haiku"
    STRONG_LLM_MODEL: str = "anthropic/claude-3-5-sonnet"
    FAST_LLM_MODEL: str = "openai/gpt-4o-mini"

    # ── Social Platforms ──────────────────────────────────────────
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""
    INSTAGRAM_APP_ID: str = ""
    INSTAGRAM_APP_SECRET: str = ""
    X_API_KEY: str = ""
    X_API_SECRET: str = ""
    X_BEARER_TOKEN: str = ""

    # ── Storage ───────────────────────────────────────────────────
    S3_ENDPOINT_URL: str = ""
    S3_ACCESS_KEY_ID: str = ""
    S3_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = "metago-media"
    S3_REGION: str = "ap-south-1"

    # ── CORS ──────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # ── Rate Limits ───────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    AUTH_RATE_LIMIT_PER_MINUTE: int = 10

    # ── Budgets ───────────────────────────────────────────────────
    DAILY_LLM_BUDGET_USD: float = 10.0
    MONTHLY_LLM_BUDGET_USD: float = 200.0

    # ── Initial Admin ─────────────────────────────────────────────
    INITIAL_ADMIN_EMAIL: str = "admin@metago.in"
    INITIAL_ADMIN_PASSWORD: str = "CHANGE_ME"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",")]
        return v

    @property
    def is_demo(self) -> bool:
        return self.OPERATING_MODE == "demo"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
