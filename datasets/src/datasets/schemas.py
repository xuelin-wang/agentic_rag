"""Pydantic models for datasets REST API."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class StoreMetadataRequest(BaseModel):
    dataset_id: UUID = Field(..., description="Unique dataset identifier.")
    metadata: dict[str, Any] = Field(..., description="Metadata values to merge or replace.")


class StoreMetadataResponse(BaseModel):
    dataset_id: UUID = Field(..., description="Unique dataset identifier.")
    status: str = Field(..., description="Operation result status.")


class UploadDatasetResponse(BaseModel):
    dataset_id: UUID = Field(..., description="Unique dataset identifier.")
    status: str = Field("uploaded", description="Operation result status.")
    filename: str = Field(..., description="Versioned filename stored on disk.")
