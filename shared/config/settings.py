import functools
from typing import TypeVar

import dotenv
from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

TSettings = TypeVar("TSettings", bound=BaseSettings)


@functools.cache
def _load_dotenv_once(env_path: str | None = None):
    if env_path:
        _ = dotenv.load_dotenv(env_path)
    else:
        _ = dotenv.load_dotenv(dotenv.find_dotenv())


def get_settings(cls: type[TSettings]) -> TSettings:
    _load_dotenv_once()
    return cls()


def get_settings_local(
    cls: type[TSettings], env_path: str = ".env.production"
) -> TSettings:
    _load_dotenv_once(env_path)
    return cls()


class OpenAISettings(BaseModel, case_sensitive=True):
    api_key: str
    api_key_assistant: str
    assistant_id: str | None = None  # Optional: Legacy Assistants API (deprecated)
    chat_model: str = "gpt-4.1-mini"  # Updated default to match Responses API
    max_tokens: int = 16_768
    base_url: str | None = None


class Settings(BaseSettings):
    pg_url: PostgresDsn
    pooler_pg_url: PostgresDsn

    redis_url: str
    anthropic_api_key: str

    openai: OpenAISettings

    logger_name: str = "gunicorn.error"
    environment: str = "production"
    log_level: str = "DEBUG"

    model_config = SettingsConfigDict(  # pyright: ignore[reportUnannotatedClassAttribute]
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=(".env", ".env.dev", ".env.production"),
    )
