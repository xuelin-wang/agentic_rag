"""Skeleton data generator implementations."""

from __future__ import annotations

from typing import Iterable, Protocol

from data_gen.config import DataGenerationConfig


class BaseGenerator(Protocol):
    """Protocol for generator implementations."""

    def generate(self, config: DataGenerationConfig) -> Iterable[str]: ...


class SyntheticGenerator:
    """Placeholder generator that yields formatted strings."""

    def generate(self, config: DataGenerationConfig) -> Iterable[str]:
        for template in config.templates:
            yield template.format(**config.parameters)
