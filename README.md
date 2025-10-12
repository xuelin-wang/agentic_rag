# Run
```shell
uv run --active  -- uvicorn app.main:app --reload --port 8000
```

Test:
```shell
# Single response
curl -sS -X POST http://localhost:8000/v1/query \
  -H 'content-type: application/json' \
  -d '{"query":"hello world"}' | jq .

# Streaming (SSE) – note GET + query params
curl -N "http://localhost:8000/v1/query/stream?query=hello%20world"
```

