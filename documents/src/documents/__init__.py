"""Documents service package providing FastAPI endpoints for indexing and search."""

from documents.app import create_app

__all__ = ["create_app"]
