from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Sequence

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from sse_starlette import EventSourceResponse, JSONServerSentEvent

import core.settings
from app_api.core.config import AppSettings
from app_api.schemas import QueryRequest, QueryResponse, StreamError
from app_api.services.rag import full_answer, stream_answer

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "configs" / "local.yaml"


def load_app_settings(
    config_path: str | Path,
    env_path: str | Path | None = None,
) -> AppSettings:
    """Hydrate application settings from YAML and environment variables."""

    if env_path is not None:
        env_path = Path(env_path).expanduser()
        if not env_path.is_file():
            msg = f"Env file '{env_path}' does not exist."
            raise FileNotFoundError(msg)
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        load_dotenv()

    resolved_config_path = Path(config_path).expanduser()
    if not resolved_config_path.is_file():
        raise FileNotFoundError(resolved_config_path)
    return core.settings.load_dataclass_from_yaml(AppSettings, resolved_config_path)


def create_app(settings: AppSettings) -> FastAPI:
    """Instantiate the FastAPI application with the provided settings."""

    app = FastAPI(
        title="Agentic RAG API",
        version="0.1.0",
        default_response_class=ORJSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.settings = settings
    register_routes(app, settings)
    return app


def register_routes(app: FastAPI, settings: AppSettings) -> None:
    """Attach HTTP routes that close over the resolved settings."""

    @app.get("/", include_in_schema=False)
    async def root():  # noqa: D401 - simple health check
        return {"status": "ok"}

    @app.post(f"{settings.api_prefix}/query", response_model=QueryResponse)
    async def query(req: QueryRequest) -> QueryResponse:
        return await full_answer(req)

    @app.get(f"{settings.api_prefix}/query/stream")
    async def query_stream(
        request: Request,
        query: str,
        session_id: str | None = None,
        top_k: int = 5,
        temperature: float = 0.0,
    ):
        req = QueryRequest(
            query=query,
            session_id=session_id,
            top_k=top_k,
            temperature=temperature,
        )

        async def event_gen():
            try:
                i = 0
                async for event in stream_answer(req):
                    if await request.is_disconnected():
                        break
                    payload = event.model_dump()
                    event_type = payload.get("type")

                    if event_type == "chunk":
                        i += 1
                        payload["index"] = i
                        yield JSONServerSentEvent(payload)
                    elif event_type == "final":
                        yield JSONServerSentEvent(payload)
                    else:
                        yield JSONServerSentEvent(
                            {
                                "type": "error",
                                "message": (
                                    f"unknown event type: {event_type or type(event).__name__}"
                                ),
                            }
                        )
            except Exception as exc:  # pylint: disable=broad-except
                error_payload = StreamError(type="error", message=str(exc)).model_dump()
                yield JSONServerSentEvent(error_payload)

        return EventSourceResponse(
            event_gen(),
            ping=settings.sse_ping_seconds,
            send_timeout=settings.sse_send_timeout_seconds,
            headers={
                "Cache-Control": "no-cache",
                # Helpful for Nginx/Traefik to avoid buffering SSE
                "X-Accel-Buffering": "no",
            },
        )


def serve() -> None:
    """Expose an app runner compatible with setuptools entry points."""
    import uvicorn

    args = parse_args()
    application, settings = build_app(args.config, args.env)

    try:
        uvicorn.run(
            application,
            host=settings.host,
            port=settings.port,
            reload=False,
        )
    except TypeError as exc:
        if "loop_factory" not in str(exc):
            raise

        config = uvicorn.Config(
            app=application,
            host=settings.host,
            port=settings.port,
            reload=False,
        )
        server = uvicorn.Server(config)
        asyncio.run(server.serve())


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for configuring the API entry point."""

    parser = argparse.ArgumentParser(description="Run the Agentic RAG API server.")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the YAML configuration file.",
    )
    parser.add_argument(
        "--env",
        type=str,
        default=None,
        help="Path to an env file to load before parsing configuration.",
    )
    args = parser.parse_args(argv)

    config_path = Path(args.config).expanduser()
    if not config_path.is_file():
        parser.error(f"Configuration file '{config_path}' does not exist.")
    args.config = config_path

    if args.env is not None:
        env_path = Path(args.env).expanduser()
        if not env_path.is_file():
            parser.error(f"Env file '{env_path}' does not exist.")
        args.env = env_path

    return args


def build_app(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    env_path: str | Path | None = None,
) -> tuple[FastAPI, AppSettings]:
    """Convenience helper for constructing the API app."""

    settings = load_app_settings(config_path=config_path, env_path=env_path)
    return create_app(settings), settings


if __name__ == "__main__":
    serve()
