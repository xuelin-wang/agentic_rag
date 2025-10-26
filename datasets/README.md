# Datasets Service

This subproject provides a FastAPI scaffold for datasets-related capabilities in Agentic RAG. It mirrors
the template service structure with shared configuration loading and logging helpers from `core`.

## Quickstart

```shell
uv run --active -m datasets.app --config src/datasets/configs/local.yaml
```

To load environment overrides:

```shell
uv run --active -m datasets.app \
  --config src/datasets/configs/local.yaml \
  --env src/datasets/configs/local.env
```

## Development

1. `uv sync --active --extra dev`
2. `uv run --active pytest`
3. `uvx ruff check --fix .`
4. `uvx ruff format .`

Extend `datasets/app.py` as needed by updating `AppSettings`, registering additional routers, and
adding domain-specific services.
