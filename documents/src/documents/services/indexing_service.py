"""Minimal in-memory document indexing service built on top of LlamaIndex."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.schema import TextNode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from documents.schemas import DocumentPayload, SearchResult
from documents.services.settings import DocumentSettings


class DocumentIndexNotReadyError(RuntimeError):
    """Raised when a search is attempted before building the index."""


class DocumentIndexService:
    """Coordinates document ingestion and querying through LlamaIndex."""

    def __init__(self, settings: DocumentSettings) -> None:
        self._documents: dict[str, DocumentPayload] = {}
        self._index: VectorStoreIndex | None = None
        self._embed_model = HuggingFaceEmbedding(model_name=settings.embed.model_name)
        Settings.embed_model = self._embed_model

    def index_documents(self, documents: Iterable[DocumentPayload]) -> int:
        """Persist the provided documents in-memory and rebuild the index."""

        for payload in documents:
            self._documents[payload.document_id] = payload

        if not self._documents:
            self._index = None
            return 0

        nodes = [self._payload_to_node(payload) for payload in self._documents.values()]
        self._index = VectorStoreIndex(nodes=nodes)
        return len(self._documents)

    def search(self, query: str, *, limit: int) -> list[SearchResult]:
        """Execute a semantic search against the stored index."""

        if self._index is None:
            raise DocumentIndexNotReadyError("Document index has not been built yet.")

        query_engine = self._index.as_query_engine(similarity_top_k=limit)
        response = query_engine.query(query)
        return self._convert_response(response)

    def _payload_to_node(self, payload: DocumentPayload) -> TextNode:
        metadata = dict(payload.metadata or {})
        embedding = metadata.pop("embedding", None)
        metadata["document_id"] = payload.document_id

        node_kwargs: dict[str, Any] = {
            "id_": payload.document_id,
            "text": payload.content,
            "metadata": metadata,
        }
        if embedding is not None:
            node_kwargs["embedding"] = embedding

        node = TextNode(**node_kwargs)
        return node

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
