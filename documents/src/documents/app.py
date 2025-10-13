"""Application setup for the documents FastAPI service."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI

REPO_ROOT = Path(__file__).resolve().parents[3]
CORE_SRC = REPO_ROOT / "core" / "src"
if CORE_SRC.exists() and str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from core import configure_logging, configure_tracing  # noqa: E402

from documents.routers.indexing import router as indexing_router  # noqa: E402
from documents.routers.search import router as search_router  # noqa: E402


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="Documents API",
        description="Endpoints for document ingestion and retrieval built on LlamaIndex",
        version="0.1.0",
    )
    app.include_router(indexing_router)
    app.include_router(search_router)
    configure_tracing(app, service_name="documents-api")
    return app


app = create_app()


def serve() -> None:
    """Run the documents service with Uvicorn."""
    import uvicorn

    uvicorn.run("documents.app:app", host="0.0.0.0", port=8080, reload=False)


if __name__ == "__main__":
    serve()
