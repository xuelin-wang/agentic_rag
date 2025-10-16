"""Application setup for the documents FastAPI service."""

from __future__ import annotations

import dataclasses
from typing import TypeVar

from fastapi import FastAPI
import asyncio
import uvicorn

from core import configure_logging, configure_tracing
from core.cmd_utils import load_app_settings
from core.settings import CoreSettings

from documents.routers.indexing import router as indexing_router
from documents.routers.search import router as search_router

_SettingsT = TypeVar("_SettingsT")


@dataclasses.dataclass(frozen=True)
class AppSettings(CoreSettings):
    cors_origins: list[str] = dataclasses.field(default_factory=lambda: ["*"])
    host: str = "0.0.0.0"
    port: int = 8080


def create_app(settings: AppSettings | None = None) -> FastAPI:
    resolved_settings = settings or AppSettings()
    configure_logging()
    app = FastAPI(
        title=resolved_settings.title,
        description=resolved_settings.description,
        version=resolved_settings.version,
    )
    app.include_router(indexing_router)
    app.include_router(search_router)
    configure_tracing(app, service_name="documents-api")
    return app


def serve() -> None:
    """Run the documents service with Uvicorn."""

    settings = load_app_settings(AppSettings, None)
    application = create_app(settings)
    config = uvicorn.Config(
        application,
        host=settings.host,
        port=settings.port,
        reload=False,
    )
    server = uvicorn.Server(config=config)
    asyncio.run(server.serve())


if __name__ == "__main__":
    serve()
