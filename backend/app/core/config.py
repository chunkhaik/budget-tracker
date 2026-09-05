from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "budget-tracker"
    app_env: str = "development"
    api_v1_prefix: str = "/v1"
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/budget_tracker"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672//"
    transaction_queue_name: str = "transaction_commands"

    default_currency_code: str = "USD"
    dev_current_user_id: str = "00000000-0000-0000-0000-000000000001"
    dev_current_user_email: str = "dev-user@example.com"
    dev_current_user_name: str = "Dev User"

    broker_connection_retry_on_startup: bool = True
    health_timeout_seconds: int = 5
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
