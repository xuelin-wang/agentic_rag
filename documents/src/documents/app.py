"""Application setup for the documents FastAPI service."""

from fastapi import FastAPI

from documents.logging_setup import configure_logging
from documents.routers.indexing import router as indexing_router
from documents.routers.search import router as search_router
from documents.telemetry import configure_tracing


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="Documents API",
        description="Endpoints for document ingestion and retrieval built on LlamaIndex",
        version="0.1.0",
    )
    app.include_router(indexing_router)
    app.include_router(search_router)
    configure_tracing(app)
    return app


app = create_app()


def serve() -> None:
    """Run the documents service with Uvicorn."""
    import uvicorn

    uvicorn.run("documents.app:app", host="0.0.0.0", port=8080, reload=False)


if __name__ == "__main__":
    serve()
