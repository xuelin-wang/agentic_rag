# RAG Agent

This subproject contains a retrieval-augmented generation (RAG) agent implementation built on top of `llama-index`.

## Features
- Lazily builds a `VectorStoreIndex` from a document loader
- Provides a simple interface for answering natural language questions against the index
- Integrates with shared utilities published from the `core` package

## Getting Started
1. Create a virtual environment and install this package in editable mode:

   ```bash
   uv pip install -e ../core
   uv pip install -e .
   ```

2. Place your unstructured data inside a directory (for example `./data`).
3. Run the demo CLI:

   ```bash
   rag-agent-demo --data-path ./data "What does the documentation say about onboarding?"
   ```

## Environment
The agent relies on global `llama-index` settings (LLM, embedding-model, etc.) configured by the shared `agent_core` helpers. See `core/README.md` for instructions on configuring providers.
