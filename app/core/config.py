
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_prefix: str = "/v1"
    cors_origins: list[str] = ["*"]
    sse_ping_seconds: int = 15
    sse_send_timeout_seconds: int | None = 30


model_config = SettingsConfigDict(
    env_file=".env",
    env_prefix="RAG_",
    extra="ignore",
)

settings = Settings()
