"""Analytics agent built on top of LlamaIndex's pandas query engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

import pandas as pd

from agent_core.context import AgentContext, AgentResponse


@dataclass(slots=True)
class AnalyticsAgentConfig:
    """Configuration for building an analytics agent."""

    dataframe: pd.DataFrame
    table_name: str = "analytics_table"
    description: str | None = None


def _default_query_engine(config: AnalyticsAgentConfig) -> Any:
    try:
        from llama_index.experimental.query_engine import PandasQueryEngine
    except ImportError as exc:
        raise RuntimeError("llama-index experimental extras are required for analytics mode") from exc

    return PandasQueryEngine(df=config.dataframe, verbose=False)


class AnalyticsAgent:
    """Thin wrapper around the Pandas query engine."""

    def __init__(
        self,
        config: AnalyticsAgentConfig,
        *,
        query_engine_factory: Callable[[AnalyticsAgentConfig], Any] | None = None,
    ) -> None:
        self._config = config
        self._query_engine_factory = query_engine_factory or _default_query_engine
        self._engine = self._query_engine_factory(config)

    def query(
        self,
        prompt: str,
        *,
        context: AgentContext | None = None,
        engine_kwargs: Mapping[str, Any] | None = None,
    ) -> AgentResponse:
        kwargs: dict[str, Any] = {}
        if engine_kwargs:
            kwargs.update(engine_kwargs)

        response = self._engine.query(prompt, **kwargs)
        message = getattr(response, "response", None)
        output = message if isinstance(message, str) else str(response)
        metadata = {
            "agent_namespace": context.namespace if context else None,
            "table": self._config.table_name,
            "description": self._config.description,
        }
        return AgentResponse(content=output, metadata=metadata)
