from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    M0 settings:
    - REDIS_URL: connection string for redis
    - RUN_TTL_S: how long to keep run records in redis (seconds)
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    REDIS_URL: str = "redis://localhost:6379/0"
    RUN_TTL_S: int = 86400


def get_settings() -> Settings:
    # In a larger app you'd cache this. M0 keeps it simple.
    return Settings()
