"""Pydantic schemas for the documents service."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class DocumentPayload(BaseModel):
    """Incoming payload describing a document to ingest."""

    document_id: str = Field(..., description="Client-supplied document identifier")
    content: str = Field(..., description="Raw document content")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Optional metadata fields stored alongside the document"
    )


class IndexDocumentsRequest(BaseModel):
    """Request body for indexing a batch of documents."""

    documents: list[DocumentPayload] = Field(
        ..., description="Collection of documents that should be persisted and indexed"
    )


class IndexDocumentsResponse(BaseModel):
    """Response body returned after indexing documents."""

    indexed_count: int = Field(..., description="Number of documents now tracked by the index")


class DocumentUploadResponse(BaseModel):
    """Response returned after accepting a PDF upload for indexing."""

    document_id: str = Field(..., description="Identifier assigned to the uploaded document")
    file_path: str = Field(..., description="Filesystem path where the uploaded file is stored")
    status: Literal["accepted"] = Field(
        "accepted",
        description="Indicates the server scheduled asynchronous extraction and indexing",
    )


class SearchRequest(BaseModel):
    """Request body for free-text document search."""

    query: str = Field(..., description="End-user query to run against the index")
    limit: int = Field(
        5,
        ge=1,
        le=20,
        description="Maximum number of matches returned by the search endpoint",
    )


class SearchResult(BaseModel):
    """A single search hit returned by LlamaIndex."""

    document_id: str = Field(..., description="Identifier of the source document")
    score: float = Field(..., description="Relevance score for the result")
    content: str | None = Field(
        default=None,
        description="Snippet pulled from the source node that matched the query",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Metadata associated with the matched node"
    )


class SearchResponse(BaseModel):
    """Response body returned after executing a search query."""

    results: list[SearchResult] = Field(..., description="Ordered list of search hits")
