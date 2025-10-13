"""Helpers for configuring LlamaIndex globals in one place."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class LlamaSettings:
    """Mutable collection of global LlamaIndex settings."""

    llm: Any | None = None
    embed_model: Any | None = None
    callback_manager: Any | None = None
    prompt_helper: Any | None = None


def apply_settings(settings) -> None:
    """Apply the provided settings to the global LlamaIndex configuration."""

    pass
