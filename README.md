# Agentic RAG Workspace

Polyrepo that hosts several focused subprojects working together to deliver an agentic retrieval-augmented system.

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
