# Core

Shared utilities and abstractions that glue the RAG and analytics agents together.

## Modules
- `core.context`: Common data structures for agent requests and responses
- `core.settings`: Helpers for applying global configuration
- `core.registry`: Lightweight registry for wiring agents into applications

## Usage
Install in editable mode alongside the agents:

```bash
uv pip install -e .
```

Reference the helpers when orchestrating agent workflows:

```python
from core.context import Context
from core.settings import CoreSettings

context = Context(namespace="rag-pipeline")
```
