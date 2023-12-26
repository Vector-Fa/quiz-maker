from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environments(Enum):
    DEV = "development"
    PRODUCTION = "production"


class Settings(BaseSettings):
    ENVIRONMENT: Environments
    DATABASE_URL: str
    REDIS_URL: str

    EMAIL_HOST: str
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str
    EMAIL_HOST_PORT: int

    SECRET_KEY: str
    ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file="src/core/.env", env_file_encoding="utf-8"
    )


settings: Settings = Settings()
