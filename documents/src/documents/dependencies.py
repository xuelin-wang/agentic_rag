"""Dependency providers for the documents service."""

from functools import lru_cache

from documents.services.indexing_service import DocumentIndexService


@lru_cache(maxsize=1)
def get_document_index_service() -> DocumentIndexService:
    """Return a singleton instance of the document index service."""
    return DocumentIndexService()
