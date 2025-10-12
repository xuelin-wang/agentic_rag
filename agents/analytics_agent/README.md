# Analytics Agent

This subproject provides a structured data analytics agent powered by `llama-index`.

## Highlights
- Wraps the `PandasQueryEngine` to answer natural language questions over tabular data
- Uses shared context helpers from the `core` package for consistent interfaces
- Ships with a demonstration CLI for experimentation

## Quickstart
1. Install the shared utilities and the agent in editable mode:

   ```bash
   uv pip install -e ../core
   uv pip install -e .
   ```

2. Prepare a CSV file and run the demo:

   ```bash
   analytics-agent-demo --csv ./data/sales.csv "What is the average order value?"
   ```

## Notes
The agent defers configuration of embedding and LLM providers to the shared `agent_core` package. Configure your provider keys before invoking the agent.
