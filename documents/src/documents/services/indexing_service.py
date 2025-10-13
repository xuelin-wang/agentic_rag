"""Minimal in-memory document indexing service built on top of LlamaIndex."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from llama_index.core import Document, VectorStoreIndex

from documents.schemas import DocumentPayload, SearchResult


class DocumentIndexNotReadyError(RuntimeError):
    """Raised when a search is attempted before building the index."""


class DocumentIndexService:
    """Coordinates document ingestion and querying through LlamaIndex."""

    def __init__(self) -> None:
        self._documents: dict[str, DocumentPayload] = {}
        self._index: VectorStoreIndex | None = None

    def index_documents(self, documents: Iterable[DocumentPayload]) -> int:
        """Persist the provided documents in-memory and rebuild the index."""

        for payload in documents:
            self._documents[payload.document_id] = payload

        if not self._documents:
            self._index = None
            return 0

        llama_documents = [
            Document(
                doc_id=payload.document_id,
                text=payload.content,
                metadata=payload.metadata,
            )
            for payload in self._documents.values()
        ]
        self._index = VectorStoreIndex.from_documents(llama_documents)
        return len(self._documents)

    def search(self, query: str, *, limit: int) -> list[SearchResult]:
        """Execute a semantic search against the stored index."""

        if self._index is None:
            raise DocumentIndexNotReadyError("Document index has not been built yet.")

        query_engine = self._index.as_query_engine(similarity_top_k=limit)
        response = query_engine.query(query)
        return self._convert_response(response)

    def _convert_response(self, response: Any) -> list[SearchResult]:
        """Map a LlamaIndex response object into API response models."""

        results: list[SearchResult] = []
        source_nodes = getattr(response, "source_nodes", []) or []

        for node in source_nodes:
            metadata = getattr(node, "metadata", {}) or {}
            score = float(getattr(node, "score", 0.0) or 0.0)
            content = getattr(node, "text", None)
            document_id = metadata.get("document_id") or getattr(node, "node_id", "unknown")

            if document_id in self._documents:
                payload = self._documents[document_id]
                metadata = {**payload.metadata, **metadata}
                if content is None:
                    content = payload.content

            results.append(
                SearchResult(
                    document_id=document_id,
                    score=score,
                    content=content,
                    metadata=metadata,
                )
            )

        return results

    @property
    def indexed_count(self) -> int:
        """Return the number of documents currently tracked by the service."""

        return len(self._documents)
