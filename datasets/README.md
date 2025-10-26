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
  
# store metadata
curl -X POST http://localhost:8100/v1/datasets/storeMetadata \
    -H 'Content-Type: application/json' \
    -H 'X-Metadata-Mode: overlay' \
    -d '{
          "dataset_id": "123e4567-e89b-12d3-a456-426614174000",
          "metadata": {
            "description": "Updated notes",
            "tags": ["alpha", "beta"]
          }
        }'

# upload file
curl -X POST http://localhost:8100/v1/datasets/uploadFile \
    -F "dataset_id=123e4567-e89b-12d3-a456-426614174000" \
    -F "file=@/home/xuelin/Downloads/user.yaml;type=application/octet-stream"

```

## Development

1. `uv sync --active --extra dev`
2. `uv run --active pytest`
3. `uvx ruff check --fix .`
4. `uvx ruff format .`

Extend `datasets/app.py` as needed by updating `AppSettings`, registering additional routers, and
adding domain-specific services.

## API

- `POST /v1/datasets/storeMetadata` – create or update metadata for a dataset. The UUID directory is created as needed. Supply header `X-Metadata-Mode: overlay` to merge fields, otherwise metadata is replaced (`override`).
- `POST /v1/datasets/uploadFile` – upload a new version of the dataset file. The service stores a timestamped copy and keeps `data.bin` pointed at the latest version.
