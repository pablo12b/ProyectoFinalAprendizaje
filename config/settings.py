"""
Business Backend Settings.

Pydantic BaseSettings for environment variable management.
Uses the same database as agent/ but with its own configuration.
"""

import functools

import dotenv
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


@functools.cache
def _load_dotenv_once() -> None:
    """Load .env file once."""
    dotenv.load_dotenv(dotenv.find_dotenv())


class BusinessSettings(BaseSettings):
    """Settings for Business Backend service."""

    # Database - same as agent/ (reuses PG_URL)
    pg_url: PostgresDsn

    # OpenAI settings for LLM service (optional)
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    openai_max_tokens: int = 1024

    # Feature flags for modularity
    llm_enabled: bool = True

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_prefix="",  # No prefix, uses same vars as agent
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=(".env", ".env.dev", ".env.production"),
    )


@functools.cache
def get_business_settings() -> BusinessSettings:
    """Get cached BusinessSettings instance."""
    _load_dotenv_once()
    return BusinessSettings()
