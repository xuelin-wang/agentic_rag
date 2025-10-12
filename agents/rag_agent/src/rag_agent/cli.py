"""Entry points for the `rag-agent-demo` console script."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from agent_core.context import AgentContext

from .agent import RAGAgent, RAGAgentConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interact with the RAG agent over a dataset.")
    parser.add_argument("prompt", help="Question to send to the agent")
    parser.add_argument(
        "--data-path",
        type=Path,
        default=Path("./data"),
        help="Directory containing raw documents",
    )
    parser.add_argument(
        "--response-mode",
        default="compact",
        help="Response mode passed to the query engine",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = RAGAgentConfig(data_path=args.data_path, response_mode=args.response_mode)
    agent = RAGAgent(config)
    context = AgentContext(namespace="rag", metadata={"source": str(args.data_path)})
    response = agent.query(args.prompt, context=context)
    print(response.content)


if __name__ == "__main__":  # pragma: no cover
    main()
