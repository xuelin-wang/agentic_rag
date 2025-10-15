import dataclasses
from core.settings import CoreSettings

@dataclasses.dataclass(frozen=True)
class AppSettings(CoreSettings):
    api_prefix: str = "/v1"
    cors_origins: list[str] = dataclasses.field(default_factory=lambda: ["*"])
    sse_ping_seconds: int = 15
    sse_send_timeout_seconds: int = 30
    host: str = "0.0.0.0"
    port: int = 8000
