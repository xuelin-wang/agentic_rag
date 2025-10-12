"""Utilities for standing up a retrieval-augmented agent with LlamaIndex."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, MutableMapping, Protocol

from agent_core.context import AgentContext, AgentResponse


class SupportsLoadDocuments(Protocol):
    """Protocol for loaders that provide LlamaIndex documents."""

    def load_data(self) -> Iterable[Any]:
        ...


@dataclass(slots=True)
class RAGAgentConfig:
    """Configuration controlling how the RAG agent sources and queries context."""

    data_path: Path
    response_mode: str = "compact"
    query_kwargs: Mapping[str, Any] | None = None


def build_default_index(data_path: Path):
    """Create a `VectorStoreIndex` by reading documents from ``data_path``."""

    try:
        from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
    except ImportError as exc:
        raise RuntimeError("llama-index is required to build the default index") from exc

    reader: SupportsLoadDocuments = SimpleDirectoryReader(input_dir=str(data_path))
    documents = list(reader.load_data())
    if not documents:
        msg = f"no documents found in {data_path!s}"
        raise ValueError(msg)

    return VectorStoreIndex.from_documents(documents)


class RAGAgent:
    """Simple façade over a LlamaIndex query engine suitable for RAG workflows."""

    def __init__(
        self,
        config: RAGAgentConfig,
        *,
        index_factory: Callable[[Path], Any] | None = None,
        query_engine_factory: Callable[[Any, Mapping[str, Any]], Any] | None = None,
    ) -> None:
        self._config = config
        self._index_factory = index_factory or build_default_index
        self._query_engine_factory = query_engine_factory or _default_query_engine
        self._index: Any | None = None

    def _ensure_index(self) -> Any:
        if self._index is None:
            self._index = self._index_factory(self._config.data_path)
        return self._index

    def query(self, prompt: str, *, context: AgentContext | None = None) -> AgentResponse:
        index = self._ensure_index()
        query_kwargs: MutableMapping[str, Any] = {"response_mode": self._config.response_mode}
        if self._config.query_kwargs:
            query_kwargs.update(self._config.query_kwargs)

        engine = self._query_engine_factory(index, query_kwargs)
        raw_response = engine.query(prompt)
        message = getattr(raw_response, "response", None)
        output = message if isinstance(message, str) else str(raw_response)
        metadata: dict[str, Any] = {
            "source_nodes": getattr(raw_response, "source_nodes", None),
            "agent_namespace": context.namespace if context else None,
        }
        return AgentResponse(content=output, metadata=metadata)


def _default_query_engine(index: Any, query_kwargs: Mapping[str, Any]) -> Any:
    try:
        engine = index.as_query_engine(
            response_mode=query_kwargs.get("response_mode", "compact"),
            **{k: v for k, v in query_kwargs.items() if k != "response_mode"},
        )
    except AttributeError as exc:
        msg = "Index object does not provide an `as_query_engine` method."
        raise TypeError(msg) from exc
    return engine
