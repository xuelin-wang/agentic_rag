"""Skeleton evaluation runner."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from eval_suite.metrics import EvaluationMetric, MetricResult


@dataclass(slots=True)
class EvaluationScenario:
    """Minimal scenario definition for agent evaluation."""

    prompt: str
    reference: str


@dataclass(slots=True)
class EvaluationRunner:
    """Coordinates running metrics across scenarios."""

    metrics: Sequence[EvaluationMetric]

    def run(self, scenarios: Iterable[EvaluationScenario]) -> list[MetricResult]:
        results: list[MetricResult] = []
        for scenario in scenarios:
            for metric in self.metrics:
                result = metric.compute("", scenario.reference)
                results.append(result)
        return results
