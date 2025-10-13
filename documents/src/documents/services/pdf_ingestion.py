"""Utilities for persisting and indexing uploaded PDF documents."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Final
from uuid import uuid4

from fastapi import UploadFile
from pypdf import PdfReader

from documents.schemas import DocumentPayload
from documents.services.indexing_service import DocumentIndexService

LOGGER: Final = logging.getLogger(__name__)


def _default_upload_root() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "uploads"


def get_upload_directory() -> Path:
    """Return the directory used to store uploaded files."""

    configured = os.getenv("DOCUMENTS_UPLOAD_DIR")
    return Path(configured) if configured else _default_upload_root()


async def persist_pdf_upload(
    upload: UploadFile,
    *,
    document_id: str | None = None,
) -> tuple[str, Path]:
    """Persist the uploaded PDF to disk and return its document id and path."""

    doc_id = document_id or str(uuid4())
    destination_dir = get_upload_directory()
    destination_dir.mkdir(parents=True, exist_ok=True)

    original_suffix = Path(upload.filename or "").suffix or ".pdf"
    target_path = destination_dir / f"{doc_id}{original_suffix}"

    content = await upload.read()
    if not content:
        raise ValueError("Uploaded PDF is empty.")

    target_path.write_bytes(content)
    await upload.close()

    return doc_id, target_path


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text content from a PDF file."""

    reader = PdfReader(str(file_path))
    texts: list[str] = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text:
            texts.append(page_text.strip())

    return "\n\n".join(texts)


def process_pdf_for_indexing(
    file_path: Path,
    *,
    document_id: str,
    service: DocumentIndexService,
    original_filename: str | None,
) -> None:
    """Extract content from the PDF and index it with the provided service."""

    try:
        text_content = extract_text_from_pdf(file_path)
    except Exception as exc:  # pragma: no cover - defensive logging
        LOGGER.exception("Failed to extract text from PDF %s: %s", file_path, exc)
        return

    metadata = {
        "source_path": str(file_path),
    }
    if original_filename:
        metadata["original_filename"] = original_filename

    payload = DocumentPayload(
        document_id=document_id,
        content=text_content,
        metadata=metadata,
    )

    try:
        service.index_documents([payload])
    except Exception as exc:  # pragma: no cover - defensive logging
        LOGGER.exception("Failed to index document %s: %s", document_id, exc)
