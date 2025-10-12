# Agent Core

Shared utilities and abstractions that glue the RAG and analytics agents together.

## Modules
- `agent_core.context`: Common data structures for agent requests and responses
- `agent_core.settings`: Helpers for applying global `llama-index` configuration
- `agent_core.registry`: Lightweight registry for wiring agents into applications

## Usage
Install in editable mode alongside the agents:

```bash
uv pip install -e .
```

Reference the helpers when orchestrating agent workflows:

```python
from agent_core.context import AgentContext
from agent_core.settings import apply_llama_settings, LlamaSettings

apply_llama_settings(LlamaSettings(llm_model="gpt-4o-mini"))
context = AgentContext(namespace="rag-pipeline")
```
