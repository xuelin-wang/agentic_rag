"""Template package for FastAPI-based Agentic RAG services."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any, Final

__all__ = ["AppSettings", "create_app", "serve"]

_EXPORTED_ATTRS: Final = set(__all__)

if TYPE_CHECKING:  # pragma: no cover - only for type checkers
    from .app import AppSettings, create_app, serve


def __getattr__(name: str) -> Any:
    if name in _EXPORTED_ATTRS:
        module = import_module("app_template.app")
        return getattr(module, name)
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)


def __dir__() -> list[str]:
    return sorted(set(globals()) | _EXPORTED_ATTRS)
