"""Placeholder settings helpers for agents."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AgentSettings:
    """Skeleton settings container for agent-wide configuration."""

    provider: str | None = None
    model: str | None = None


def apply_agent_settings(settings: AgentSettings) -> None:
    """Stub hook for applying global settings to agent frameworks."""

    _ = settings  # Prevent unused argument warnings until implemented.
