from pydantic import computed_field
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

    # Security
    SECRET_KEY: str = "default_secret_key_to_change_in_production"


settings = Settings()
