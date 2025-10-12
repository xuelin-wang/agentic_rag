"""Skeleton evaluation reporting utilities."""

from __future__ import annotations

from dataclasses import dataclass

from eval_suite.metrics import MetricResult


@dataclass(slots=True)
class EvaluationReport:
    """Represents an aggregate report of metric results."""

    results: list[MetricResult]


def render_report(report: EvaluationReport) -> str:
    """Render a human-readable report."""

    lines = ["Evaluation Report"]
    for result in report.results:
        value = "n/a" if result.value is None else f"{result.value:.2f}"
        lines.append(f"- {result.name}: {value}")
    return "\n".join(lines)
