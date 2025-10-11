from __future__ import annotations
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from sse_starlette import EventSourceResponse, JSONServerSentEvent
from .schemas import QueryRequest, QueryResponse, StreamChunk, StreamFinal, StreamError
from .core.config import settings
from .services.rag import stream_answer, full_answer

app = FastAPI(
    title="Agentic RAG API",
    version="0.1.0",
    default_response_class=ORJSONResponse,
)

# CORS for browser UIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def root():
    return {"status": "ok"}


# --- Non-streaming endpoint (POST) ----------------------------------------------------
@app.post(f"{settings.api_prefix}/query", response_model=QueryResponse)
async def query(req: QueryRequest) -> QueryResponse:
    return await full_answer(req)


# --- Streaming endpoint (GET + SSE) ---------------------------------------------------
# NOTE: EventSource in browsers only supports GET; pass small inputs via query params.
# For larger payloads, create a ticket first (POST) then stream by ticket id.
@app.get(f"{settings.api_prefix}/query/stream")
async def query_stream(request: Request, query: str, session_id: str | None = None, top_k: int = 5,
                       temperature: float = 0.0):
    req = QueryRequest(query=query, session_id=session_id, top_k=top_k, temperature=temperature)

    async def event_gen():
        try:
            i = 0
            async for event in stream_answer(req):
                if await request.is_disconnected():
                    break
                i += 1
                # Use JSONServerSentEvent for correct SSE framing of JSON
                if isinstance(event, StreamChunk):
                    yield JSONServerSentEvent({"type": event.type, "delta": event.delta, "index": i}).model_dump()
                elif isinstance(event, StreamFinal):
                    yield JSONServerSentEvent(event.model_dump()).model_dump()
                else:
                    # Shouldn't happen in this stub; left for completeness
                    yield JSONServerSentEvent({"type": "error", "message": "unknown event"}).model_dump()
        except Exception as exc:  # pylint: disable=broad-except
            yield JSONServerSentEvent(StreamError(type="error", message=str(exc)).model_dump()).model_dump()

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
