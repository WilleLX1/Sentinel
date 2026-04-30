from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    dashboard_database_url: str = "sqlite:///./data/sentinel.db"
    dashboard_encryption_key: str | None = None
    dashboard_session_secret: str = "change_this_to_a_long_random_secret"
    dashboard_admin_username: str = "admin"
    dashboard_admin_password: str = "sentinel-admin"
    dashboard_admin_password_hash: str | None = None
    poll_interval_seconds: int = 15
    metric_retention_days: int = 30
    agent_request_timeout_seconds: float = 6.0
    frontend_dist_path: str = "../frontend/dist"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    backups_dir: str = "./backups"

    discord_webhook_url: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_to: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

