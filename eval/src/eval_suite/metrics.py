"""Skeleton metric definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class MetricResult:
    """Represents the outcome of evaluating a metric."""

    name: str
    value: float | None
    details: dict[str, float] | None = None


class EvaluationMetric(Protocol):
    """Protocol for evaluation metrics."""

    name: str

    def compute(self, prediction: str, reference: str) -> MetricResult: ...
