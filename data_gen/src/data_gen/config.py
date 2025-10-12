"""Skeleton configuration for data generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence


@dataclass(slots=True)
class DataGenerationConfig:
    """Configuration parameters for synthetic data generation."""

    templates: Sequence[str] = field(default_factory=list)
    parameters: Mapping[str, str] = field(default_factory=dict)
