"""Application setup for the documents FastAPI service."""

from __future__ import annotations

import pydantic.dataclasses as pydantic_dataclasses
import dataclasses
import structlog
from typing import Final, TypeVar

from fastapi import FastAPI
import asyncio
import uvicorn

from core import configure_logging, configure_tracing
from core.cmd_utils import load_app_settings
from core.settings import CoreSettings

from documents.dependencies import configure_document_dependencies
from documents.routers.indexing import create_indexing_router
from documents.routers.search import create_search_router
from documents.services.settings import DocumentSettings

LOGGER: Final = structlog.get_logger(__name__)

_SettingsT = TypeVar("_SettingsT")


@pydantic_dataclasses.dataclass(frozen=True)
class AppSettings(CoreSettings):
    documents: DocumentSettings = DocumentSettings()
    cors_origins: list[str] = dataclasses.field(default_factory=lambda: ["*"])
    host: str = "0.0.0.0"
    port: int = 8080


def create_app(settings: AppSettings) -> FastAPI:
    app = FastAPI(
        title=settings.title,
        description=settings.description,
        version=settings.version,
    )

    configure_document_dependencies(settings.documents)

    indexing_router = create_indexing_router(settings.documents)
    app.include_router(indexing_router)

    search_router = create_search_router()
    app.include_router(search_router)

    configure_tracing(app, service_name="documents-api")
    return app


def serve() -> None:
    """Run the documents service with Uvicorn."""

    settings: AppSettings = load_app_settings(AppSettings, None)
    configure_logging(settings.logging)

    LOGGER.debug("settings", settings=settings)

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
