from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # In a docker-compose environment, the environment variables are not read from the .env file
        # This is because the .env file is not mounted in the container (see dockerignore file).
        # Instead, the environment variables are added to the environment with the line "env_file=../.env.dev" in the docker-compose file.
        # They are then read from the environment by the Settings class.
    )

    DATABASE_URL: str
    DEBUG: bool = False
    SECRET_KEY: str = "default_secret_key_to_change_in_production"


settings = Settings()
