# Agentic RAG Workspace

Polyrepo that hosts several focused subprojects working together to deliver an agentic retrieval-augmented system.

## Todo
- a simple rag agent using llamaindex library. Must be able to load a pdf file, have summaries for each chunk, 
and when search, must combine BM25 that searches the summaries and vector search to get best matches of relevant
chunks for a query
  - all in app_api subproject, load a pdf, do all processing
  - when query, search it and get relevant parts
  - summarize/rephrase to reply
  - send it back to user
- A datasets agent that search categories of existing datasets to find relevant datasets for a query.
- A simple data analytics agent that takes a dataset and drive stats / plots for a query.
## Layout
- `app_api/` – FastAPI service that exposes the orchestration layer
- `core/` – Shared utilities (`agent_core`) reused by downstream agents
- `agents/rag_agent/` – Retrieval-augmented generation agent built on LlamaIndex
- `agents/analytics_agent/` – Analytics agent for tabular insights

Each subproject is an isolated Python package with its own `pyproject.toml` so you can install, test, and release them independently.

## Development Workflow
- Python 3.12 with `uv` for dependency management (see `AGENTS.md` for conventions)
- Format & lint with Ruff: `uvx ruff check --fix .` then `uvx ruff format .`
- Run subproject-specific tasks from within each directory or orchestrate using your preferred tooling

## Next Steps
- Configure your preferred LLM + embedding providers through `agent_core.settings.apply_llama_settings`
- Start wiring agents together via `agent_core.registry.AgentRegistry`
- Extend the agents with datastore connectors, tools, and application-specific logic
