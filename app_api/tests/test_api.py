from __future__ import annotations

import json

from fastapi.testclient import TestClient


def test_root_health(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_returns_answer(client: TestClient) -> None:
    request_payload = {"query": "who are you?"}
    response = client.post("/v1/query", json=request_payload)

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"].startswith("Agentic RAG reply to: who are you?")
    assert payload["citations"] == ["demo://stub"]


def test_query_stream_emits_chunks_and_final_event(client: TestClient) -> None:
    with client.stream("GET", "/v1/query/stream", params={"query": "ping"}) as response:
        assert response.status_code == 200

        chunks: list[str] = []
        final_payload: dict[str, str] | None = None

        for line in response.iter_lines():
            if not line or line.startswith(":"):
                continue

            assert line.startswith("data: ")
            data = json.loads(line.removeprefix("data: "))

            if data["type"] == "chunk":
                chunks.append(data["delta"])
            elif data["type"] == "final":
                final_payload = data
                break

    assert final_payload is not None
    assert final_payload["citations"] == ["demo://stub"]
    assert "".join(chunks).strip() == final_payload["answer"]
