from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "StarScout API"
    app_version: str = "0.1.0"
    enable_docs: bool = True
    database_url: str = "postgresql://starscout:starscout_dev_password@localhost:5432/starscout"
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "fake_stars"
    analyzed_through: str = "2025-01-01"
    github_token: str | None = None
    github_repo_cache_ttl_seconds: int = 3600

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="STARSCOUT_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
