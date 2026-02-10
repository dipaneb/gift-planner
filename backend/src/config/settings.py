from functools import lru_cache
from typing import Literal

from pydantic import EmailStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # In a docker-compose environment, the environment variables are not read from the .env file.
        # This is because the .env file is not mounted in the container (see dockerignore file).
        # Instead, the environment variables are added to the environment with the line "env_file=../.env.dev" in the docker-compose file.
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

    # Security
    SECRET_KEY: str = "default_secret_key_to_change_in_production"
    REFRESH_TOKEN_TTL_DAYS: int = 30
    ACCESS_TOKEN_LIFESPAN_IN_MINUTES: int = 15

    # Used to send emails via Mailjet
    PASSWORD_RESET_TOKEN_LIFESPAN_IN_MINUTES: int
    MAILJET_API_KEY: str
    MAILJET_API_SECRET_KEY: str
    MAIL_FROM_EMAIL: EmailStr = "noreply@your-domain.com"
    MAIL_FROM_NAME: str = "Your app name"
    FRONTEND_BASE_URL: str


@lru_cache
def get_settings() -> Settings:
    return Settings()