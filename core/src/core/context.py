"""Common agent request and response payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, MutableMapping


@dataclass(slots=True)
class Context:
    """Context shared with agents when executing a task."""

    namespace: str
    metadata: MutableMapping[str, Any] = field(default_factory=dict)

    def with_metadata(self, **metadata: Any) -> "Context":
        merged = {**self.metadata, **metadata}
        return Context(namespace=self.namespace, metadata=merged)


@dataclass(slots=True)
class Response:
    """Normalized response returned from agents."""

    content: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


# Backwards compatible aliases
AgentContext = Context
AgentResponse = Response
