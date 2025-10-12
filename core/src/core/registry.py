"""Lightweight registry for composing multiple agents."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from core.context import AgentContext


class AgentRegistry:
    """Registry that maps agent identifiers to callables."""

    def __init__(self) -> None:
        self._factories: dict[str, Callable[[AgentContext], Any]] = {}

    def register(self, name: str, factory: Callable[[AgentContext], Any]) -> None:
        if name in self._factories:
            msg = f"agent '{name}' is already registered"
            raise ValueError(msg)
        self._factories[name] = factory

    def get(self, name: str) -> Callable[[AgentContext], Any]:
        try:
            return self._factories[name]
        except KeyError as exc:
            msg = f"agent '{name}' is not registered"
            raise KeyError(msg) from exc

    def build(self, name: str, context: AgentContext) -> Any:
        factory = self.get(name)
        return factory(context)

    def __contains__(self, name: object) -> bool:
        return name in self._factories
