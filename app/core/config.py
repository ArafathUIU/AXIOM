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
    enable_rate_limiting: bool = True
    ip_rate_limit_per_minute: int = 1000
    api_key_rate_limit_per_minute: int = 1000
    redis_url: str | None = None
    cors_origins: str = "*"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"
    admin_token: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
