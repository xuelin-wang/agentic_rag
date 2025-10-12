"""Skeleton pipeline for preparing knowledge base artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol


class SupportsPersist(Protocol):
    """Protocol for objects that can be persisted to disk."""

    def persist(self, output_dir: str) -> None: ...


@dataclass(slots=True)
class KnowledgeIngestConfig:
    """Configuration for preparing a knowledge base."""

    source_paths: Iterable[Path]
    output_dir: Path
    chunk_size: int = 1024


def build_index(config: KnowledgeIngestConfig) -> SupportsPersist | None:
    """Stub entry point for building an index from source documents."""

    del config  # Placeholder until integration is implemented.
    return None
