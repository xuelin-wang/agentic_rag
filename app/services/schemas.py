from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    query: str = Field(..., description="User query text")
    session_id: Optional[str] = Field(None, description="Logical session identifier")
    top_k: int = 5
    temperature: float = 0.0


class QueryResponse(BaseModel):
    answer: str
    citations: List[str] = []


class StreamChunk(BaseModel):
    type: str = "chunk"
    delta: str


class StreamFinal(BaseModel):
    type: str = "final"
    answer: str
    citations: List[str] = []


class StreamError(BaseModel):
    type: str = "error"
    message: str
