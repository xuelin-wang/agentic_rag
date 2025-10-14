# Run
```shell
uv run --active  -m app_api.main --config src/app_api/configs/local.yaml
```

Test:


pytest:
```shell 
source <repo root>/.venv/bin/activate

# ensure in the directory app_api
cd <repo root>/app_api

uv sync --active --extra dev 
uv run --active pytest
```

Manual:
```shell
# Single response
curl -sS -X POST http://localhost:8000/v1/query \
  -H 'content-type: application/json' \
  -d '{"query":"hello world"}' | jq .

# Streaming (SSE) – note GET + query params
curl -N "http://localhost:8000/v1/query/stream?query=hello%20world"
```
