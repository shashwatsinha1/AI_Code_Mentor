from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Code Mentor API"
    database_url: str = Field(
        default="sqlite+aiosqlite:///./dev.db",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    jwt_secret_key: str = Field(
        default="change-me-in-production-with-at-least-32-bytes",
        alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    openai_api_key: SecretStr | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1", alias="OPENAI_BASE_URL"
    )
    judge0_api_url: str = Field(default="https://ce.judge0.com", alias="JUDGE0_API_URL")
    judge0_auth_token: SecretStr | None = Field(default=None, alias="JUDGE0_AUTH_TOKEN")
    judge0_rapidapi_key: SecretStr | None = Field(default=None, alias="JUDGE0_RAPIDAPI_KEY")
    judge0_rapidapi_host: str | None = Field(default=None, alias="JUDGE0_RAPIDAPI_HOST")
    judge0_timeout_seconds: int = Field(default=20, alias="JUDGE0_TIMEOUT_SECONDS")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
