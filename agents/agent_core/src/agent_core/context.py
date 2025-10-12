"""Skeleton context and response payloads for agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(slots=True)
class AgentContext:
    """Minimal context passed to agents when executing a query."""

    namespace: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentResponse:
    """Simple response envelope returned by agents."""

    content: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
