"""Helpers for configuring LlamaIndex globals in one place."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class LlamaSettings:
    """Mutable collection of global LlamaIndex settings."""

    llm: Any | None = None
    embed_model: Any | None = None
    callback_manager: Any | None = None
    prompt_helper: Any | None = None


def apply_llama_settings(settings: LlamaSettings) -> None:
    """Apply the provided settings to the global LlamaIndex configuration."""

    try:
        from llama_index.core import Settings
    except ImportError as exc:
        raise RuntimeError(
            "llama-index must be installed to configure global settings"
        ) from exc

    for key, value in asdict(settings).items():
        if value is not None:
            setattr(Settings, key, value)
