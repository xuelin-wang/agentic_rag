"""FastAPI service skeleton for datasets operations."""

from __future__ import annotations

import asyncio
import dataclasses
from typing import Final
from uuid import UUID

import pydantic.dataclasses as pydantic_dataclasses
import structlog
import uvicorn
from fastapi import APIRouter, FastAPI, File, Form, Header, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from core import configure_logging
from core.cmd_utils import load_app_settings
from core.settings import CoreSettings
from datasets.FsStore import FsSettings, FsStore
from datasets.schemas import (
    StoreMetadataRequest,
    StoreMetadataResponse,
    UploadDatasetResponse,
)

LOGGER: Final = structlog.get_logger(__name__)


@pydantic_dataclasses.dataclass(frozen=True)
class AppSettings(CoreSettings):
    """Settings for the datasets service."""

    api_prefix: str = "/v1"
    cors_origins: list[str] = dataclasses.field(default_factory=lambda: ["*"])
    host: str = "0.0.0.0"
    port: int = 8080
    reload: bool = False
    service_name: str = "datasets-service"
    metadata: dict[str, str] = dataclasses.field(default_factory=dict)
    # must be one of fs: file system,
    type: str = "fs"
    fs: FsSettings = FsSettings()


def create_app(settings: AppSettings) -> FastAPI:
    """Instantiate the FastAPI application."""

    app = FastAPI(
        title=settings.title or "Datasets Service",
        description=settings.description,
        version=settings.version,
        default_response_class=ORJSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    store = FsStore(settings.fs)
    app.state.settings = settings
    app.state.store = store

    register_routes(app, settings, store)
    return app


UPDATE_METADATA_MODE_HEADER = "X-Metadata-Mode"
_VALID_METADATA_MODES = {"override", "overlay"}


def register_routes(app: FastAPI, settings: AppSettings, store: FsStore) -> None:
    """Attach router skeletons for the datasets API."""

    @app.get("/", include_in_schema=False)
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    router = APIRouter(prefix=settings.api_prefix, tags=["datasets"])

    @router.get("/ping")
    def ping() -> dict[str, str]:
        return {
            "message": "pong",
            "service": settings.service_name or "datasets-service",
        }

    @router.post(
        "/datasets/storeMetadata",
        response_model=StoreMetadataResponse,
        status_code=status.HTTP_200_OK,
    )
    def store_metadata(
        payload: StoreMetadataRequest,
        metadata_mode: str = Header(
            default="overlay",
            alias=UPDATE_METADATA_MODE_HEADER,
            description="Use 'override' to replace metadata or 'overlay' to merge fields.",
        ),
    ) -> StoreMetadataResponse:
        dataset_id = payload.dataset_id
        normalized_mode = metadata_mode.lower()
        if normalized_mode not in _VALID_METADATA_MODES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid metadata update mode '{metadata_mode}'. "
                    f"Expected one of: {', '.join(sorted(_VALID_METADATA_MODES))}."
                ),
            )

        overlay = normalized_mode == "overlay"
        created = False
        if not store.dataset_dir_exists(dataset_id):
            store.store_metadata(dataset_id, payload.metadata)
            created = True
        else:
            if overlay:
                store.update_metadata(dataset_id, payload.metadata, overlay=True)
            else:
                store.store_metadata(dataset_id, payload.metadata)

        status_label = "created" if created else "updated"
        return StoreMetadataResponse(dataset_id=dataset_id, status=status_label)

    @router.post(
        "/datasets/uploadFile",
        response_model=UploadDatasetResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_file(
        dataset_id: UUID = Form(...),
        file: UploadFile = File(...),
    ) -> UploadDatasetResponse:
        if not store.dataset_dir_exists(dataset_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset {dataset_id} does not exist.",
            )

        payload = await file.read()
        version_path = store.store_data(dataset_id, payload)
        return UploadDatasetResponse(
            dataset_id=dataset_id,
            status="uploaded",
            filename=version_path.name,
        )

    app.include_router(router)


def serve() -> None:
    """Entrypoint compatible with `python -m datasets.app`."""

    settings: AppSettings = load_app_settings(AppSettings, None)

    configure_logging(settings.logging)
    application = create_app(settings)

    LOGGER.info(
        "datasets.startup",
        host=settings.host,
        port=settings.port,
        service_name=settings.service_name,
        metadata=settings.metadata,
    )

    config = uvicorn.Config(
        app=application,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
    server = uvicorn.Server(config=config)
    asyncio.run(server.serve())


if __name__ == "__main__":  # pragma: no cover - import-time guard
    serve()
