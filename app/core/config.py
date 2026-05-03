from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AXIOM"
    app_version: str = "0.1.0"
    environment: str = "local"
    debug: bool = False
    log_level: str = "INFO"
    database_url: str = "sqlite:///./axiom.db"
    slow_response_threshold_ms: float = 1000.0
    error_rate_threshold_percent: float = 50.0
    traffic_burst_threshold_count: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
