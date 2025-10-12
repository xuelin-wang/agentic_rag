from __future__ import annotations
import asyncio
from typing import AsyncIterator
from . import schemas


# --- Replace these with your real pipeline pieces later ---
async def _fake_tokenize(text: str) -> list[str]:
    # naive tokenization for demo purposes
    return [t + " " for t in text.split()]


async def stream_answer(
    req: schemas.QueryRequest,
) -> AsyncIterator[schemas.StreamChunk | schemas.StreamFinal]:
    tokens = await _fake_tokenize(f"Agentic RAG reply to: {req.query}")
    answer_accum: list[str] = []

    for _, tok in enumerate(tokens):
        await asyncio.sleep(0.08)  # simulate work/latency
        answer_accum.append(tok)
        yield schemas.StreamChunk(delta=tok)

    final = schemas.StreamFinal(answer="".join(answer_accum).strip(), citations=["demo://stub"])
    yield final


async def full_answer(req: schemas.QueryRequest) -> schemas.QueryResponse:
    # In a real impl, call your model/tools, do retrieval/rerank, build final answer, etc.
    chunks: list[str] = []
    async for piece in stream_answer(req):
        if piece.type == "chunk":
            chunks.append(piece.delta)
    return schemas.QueryResponse(answer="".join(chunks).strip(), citations=["demo://stub"])
