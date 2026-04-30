from functools import lru_cache
import socket

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sentinel_api_key: str = "change_this_to_a_long_random_secret"
    server_name: str = socket.gethostname()
    agent_host: str = "127.0.0.1"
    agent_port: int = 8443
    log_level: str = "info"
    sentinel_actions_enabled: bool = False
    sentinel_agent_admin_key: str | None = None
    rate_limit_per_minute: int = 240
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    disk_path: str = "/"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

