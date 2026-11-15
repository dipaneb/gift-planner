from functools import lru_cache
from typing import Literal

from pydantic import EmailStr, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # In a docker-compose environment, the environment variables are not read from the .env file.
        # This is because the .env file is not mounted in the container (see dockerignore file).
        # Instead, the environment variables are added to the environment with the line "env_file=../.env" in the docker-compose file.
        # They are then read from the environment by the Settings class.
        # So there is no need for env_file=".env" here.
    )

    # Database
    DATABASE_URL: str

    # Environment
    ENV: Literal["production", "development"] = 'production'
    DEBUG: bool = False
    ENABLE_DOCS: bool = False

    @computed_field
    @property
    def SWAGGER_URL(self) -> str:
        return "/docs" if self.ENABLE_DOCS else None

    @computed_field
    @property
    def REDOC_URL(self) -> str:
        return "/redoc" if self.ENABLE_DOCS else None

    @computed_field
    @property
    def OPENAPI_URL(self) -> str:
        return "/openapi.json" if self.ENABLE_DOCS else None

    # Logging
    LOG_LEVEL: str = "INFO"

    # Trusted hosts (comma-separated). Empty = allow all (dev only).
    ALLOWED_HOSTS: str = ""

    # Security
    SECRET_KEY: str
    REFRESH_TOKEN_TTL_DAYS: int = 30
    # A refresh token rotated less than this many seconds ago can still be used once more
    # without being treated as stolen: two tabs refreshing at the same time, or a refresh
    # response lost on a flaky mobile connection, would otherwise log the user out everywhere.
    REFRESH_TOKEN_REUSE_GRACE_SECONDS: int = 60
    ACCESS_TOKEN_LIFESPAN_IN_MINUTES: int = 15

    # Used to send emails via Mailjet
    PASSWORD_RESET_TOKEN_LIFESPAN_IN_MINUTES: int = 30
    ACCOUNT_VERIFICATION_TOKEN_LIFESPAN_IN_HOURS: int = 1
    MAILJET_API_KEY: str
    MAILJET_API_SECRET_KEY: str
    MAIL_FROM_EMAIL: EmailStr = "noreply@dipane.fr"
    MAIL_FROM_NAME: str = "Gift Planner"
    # Where users can write to (email footer, and Reply-To of every email sent from MAIL_FROM_EMAIL)
    SUPPORT_EMAIL: EmailStr = "support@giftplanner.dipane.fr"
    FRONTEND_BASE_URL: str

    # Weekly visits report (Friday 20:00 Paris time). Empty = report disabled.
    ANALYTICS_REPORT_EMAIL: EmailStr | None = None

    @field_validator("ANALYTICS_REPORT_EMAIL", mode="before")
    @classmethod
    def empty_report_email_is_none(cls, value: str | None) -> str | None:
        return value or None


@lru_cache
def get_settings() -> Settings:
    return Settings()