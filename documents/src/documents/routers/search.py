"""Document retrieval endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from documents.dependencies import get_document_index_service
from documents.schemas import SearchRequest, SearchResponse
from documents.services.indexing_service import DocumentIndexNotReadyError, DocumentIndexService

router = APIRouter(prefix="/documents", tags=["search"])


@router.post("/search", response_model=SearchResponse, summary="Search documents")
async def search_documents(
    request: SearchRequest,
    service: Annotated[DocumentIndexService, Depends(get_document_index_service)],
) -> SearchResponse:
    """Query the index and return matches produced by LlamaIndex."""

    try:
        results = service.search(request.query, limit=request.limit)
    except DocumentIndexNotReadyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return SearchResponse(results=results)
