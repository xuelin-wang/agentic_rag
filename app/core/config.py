from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    api_prefix: str = "/v1"
    cors_origins: List[str] = ["*"]
    sse_ping_seconds: int = 15
    sse_send_timeout_seconds: int | None = 30


model_config = SettingsConfigDict(
    env_file=".env",
    env_prefix="RAG_",
    extra="ignore",
)

settings = Settings()
