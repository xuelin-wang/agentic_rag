"""Entry point for the datasets agent demo CLI."""

from __future__ import annotations

import argparse
from typing import Sequence

from agent_core.context import AgentContext

from datasets_agent.agent import DatasetsAgent, DatasetsAgentConfig

_DEFAULT_CATEGORIES = {
    "climate": ["climate", "weather", "temperature"],
    "demographics": ["population", "demographic", "census"],
    "health": ["health", "medical", "disease"],
    "economics": ["economy", "gdp", "finance"],
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query dataset categories for relevant leads.")
    parser.add_argument("prompt", help="Question or topic to search against the dataset catalog")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = DatasetsAgentConfig(categories=_DEFAULT_CATEGORIES)
    agent = DatasetsAgent(config)
    context = AgentContext(namespace="datasets", metadata={"source": "default-catalog"})
    response = agent.query(args.prompt, context=context)
    print(response.content)


if __name__ == "__main__":  # pragma: no cover
    main()
