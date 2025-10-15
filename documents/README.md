# Documents Service

Skeleton FastAPI service exposing document indexing and search endpoints built on top of LlamaIndex.

## Getting Started

```bash
source <repo root>/.venv/bin/activate

# ensure in the directory documents
cd <repo root>/documents

uv sync --active
uv run --active  -m documents.app --config src/documents/configs/local.yaml

# test using curl
curl -X POST http://localhost:8080/documents/index \
         -H 'Content-Type: application/json' \
         -d '{"documents":[{"document_id":"doc-1","content":"Vector databases rock","metadata":{"topic":"demo"}}]}'

curl -X POST http://localhost:8080/documents/search \
         -H 'Content-Type: application/json' \
         -d '{"query":"vector","limit":5}'


# run tests
uv sync --active --extra dev 
uv run --active  --extra dev pytest
```

