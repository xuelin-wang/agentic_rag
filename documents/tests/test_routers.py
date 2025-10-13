"""Integration-style tests for the documents API routers."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from fastapi.testclient import TestClient

from documents.schemas import SearchResult
from documents.services import pdf_ingestion

if TYPE_CHECKING:
    from .conftest import FakeDocumentIndexService


def test_index_documents_returns_indexed_count(
    client: TestClient, fake_service: FakeDocumentIndexService
) -> None:
    payload = {
        "documents": [
            {
                "document_id": "doc-1",
                "content": "Vector databases rock",
                "metadata": {"topic": "demo"},
            }
        ]
    }

    response = client.post("/documents/index", json=payload)

    assert response.status_code == 200
    assert response.json() == {"indexed_count": 1}
    assert [doc.document_id for doc in fake_service.indexed_documents] == ["doc-1"]


def test_search_documents_returns_service_results(
    client: TestClient, fake_service: FakeDocumentIndexService
) -> None:
    fake_service.results = [
        SearchResult(
            document_id="doc-1",
            score=0.87,
            content="Snippet",
            metadata={"topic": "demo"},
        )
    ]

    response = client.post(
        "/documents/search",
        json={"query": "vector", "limit": 3},
    )

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {
                "document_id": "doc-1",
                "score": 0.87,
                "content": "Snippet",
                "metadata": {"topic": "demo"},
            }
        ]
    }
    assert fake_service.search_calls[-1] == ("vector", 3)


def test_search_documents_returns_503_when_index_not_ready(
    client: TestClient, fake_service: FakeDocumentIndexService
) -> None:
    fake_service.raise_not_ready = True

    response = client.post(
        "/documents/search",
        json={"query": "vector"},
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "Document index has not been built yet."}


def test_index_pdf_upload_schedules_background_task(
    client: TestClient,
    fake_service: FakeDocumentIndexService,
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("DOCUMENTS_UPLOAD_DIR", str(tmp_path / "uploads"))

    extracted_text = "Parsed PDF content"
    captured_path: dict[str, Path] = {}

    def fake_extract(path: Path) -> str:
        captured_path["path"] = path
        return extracted_text

    monkeypatch.setattr(pdf_ingestion, "extract_text_from_pdf", fake_extract)

    response = client.post(
        "/documents/index/pdf",
        data={"document_id": "doc-upload"},
        files={"file": ("sample.pdf", b"%PDF-1.4\n...", "application/pdf")},
    )

    assert response.status_code == 202
    body = response.json()
    stored_path = Path(body["file_path"])  # type: ignore[path-type]

    assert body == {
        "document_id": "doc-upload",
        "file_path": str(stored_path),
        "status": "accepted",
    }
    assert stored_path.exists()
    assert captured_path["path"] == stored_path

    assert fake_service.indexed_documents[0].document_id == "doc-upload"
    assert fake_service.indexed_documents[0].content == extracted_text
    assert fake_service.indexed_documents[0].metadata["source_path"] == str(stored_path)
