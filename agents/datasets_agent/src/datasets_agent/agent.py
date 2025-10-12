"""Skeleton implementation of a datasets discovery agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from agent_core.context import AgentContext, AgentResponse


@dataclass(slots=True)
class DatasetsAgentConfig:
    """Configuration for the datasets agent."""

    categories: Mapping[str, Sequence[str]] = field(default_factory=dict)
    fallback_response: str = "No matching dataset categories found."


class DatasetsAgent:
    """Lightweight agent that matches user queries against dataset categories."""

    def __init__(self, config: DatasetsAgentConfig) -> None:
        self._config = config

    def query(self, prompt: str, *, context: AgentContext | None = None) -> AgentResponse:
        lower_prompt = prompt.lower()
        matches: list[str] = []

        for category, keywords in self._config.categories.items():
            if any(keyword.lower() in lower_prompt for keyword in keywords):
                matches.append(category)

        if matches:
            content = "Relevant dataset categories: " + ", ".join(sorted(matches))
        else:
            content = self._config.fallback_response

        metadata = {
            "agent_namespace": context.namespace if context else None,
            "matched_categories": matches,
        }
        return AgentResponse(content=content, metadata=metadata)
