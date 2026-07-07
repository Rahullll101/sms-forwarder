"""
Application Configuration

Loads and validates all application settings
from environment variables.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ======================================================
    # PostgreSQL
    # ======================================================

    database_host: str = Field(
        default="localhost",
        alias="DATABASE_HOST",
    )

    database_port: int = Field(
        default=5432,
        alias="DATABASE_PORT",
    )

    database_name: str = Field(
        default="gammu",
        alias="DATABASE_NAME",
    )

    database_user: str = Field(
        default="postgres",
        alias="DATABASE_USER",
    )

    database_password: str = Field(
        ...,
        alias="DATABASE_PASSWORD",
    )

    # ======================================================
    # Endpoint
    # ======================================================

    endpoint_url: str = Field(
        ...,
        alias="ENDPOINT_URL",
    )

    # ======================================================
    # Application
    # ======================================================

    request_timeout: int = Field(
        default=30,
        alias="REQUEST_TIMEOUT",
    )

    max_retry: int = Field(
        default=5,
        alias="MAX_RETRY",
    )

    retry_poll_interval: int = Field(
        default=30,
        alias="RETRY_POLL_INTERVAL",
    )

    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )


settings = Settings()