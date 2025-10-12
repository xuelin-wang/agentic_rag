"""Demo CLI for the analytics agent."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

import pandas as pd

from agent_core.context import AgentContext

from .agent import AnalyticsAgent, AnalyticsAgentConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ask questions about a CSV file.")
    parser.add_argument("prompt", help="Question to run against the dataframe")
    parser.add_argument("--csv", type=Path, required=True, help="Path to the CSV file")
    parser.add_argument(
        "--table-name",
        default="analytics_table",
        help="Logical name for the data being queried",
    )
    parser.add_argument(
        "--description",
        default=None,
        help="Optional description surfaced in analytics metadata",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    dataframe = pd.read_csv(args.csv)
    config = AnalyticsAgentConfig(
        dataframe=dataframe,
        table_name=args.table_name,
        description=args.description,
    )
    agent = AnalyticsAgent(config)
    context = AgentContext(namespace="analytics", metadata={"source": str(args.csv)})
    response = agent.query(args.prompt, context=context)
    print(response.content)


if __name__ == "__main__":  # pragma: no cover
    main()
