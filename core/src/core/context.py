"""Common agent request and response payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, MutableMapping


@dataclass(slots=True)
class AgentContext:
    """Context shared with agents when executing a task."""

    namespace: str
    metadata: MutableMapping[str, Any] = field(default_factory=dict)

    def with_metadata(self, **metadata: Any) -> "AgentContext":
        merged = {**self.metadata, **metadata}
        return AgentContext(namespace=self.namespace, metadata=merged)


@dataclass(slots=True)
class AgentResponse:
    """Normalized response returned from agents."""

    content: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
