"""
Content Repository Routes
API endpoints for content repository operations
"""

from fastapi import APIRouter, Query, HTTPException, status, Request, Body
from typing import Optional
import uuid
from pydantic import BaseModel, Field

from app.controllers.content_repository_controller import ContentRepositoryController
from app.core.response import APIResponse, safe_response_detail
from app.core.logging import get_logger

logger = get_logger("content_repository_routes")
router = APIRouter()


class UpdateRelevanceRequest(BaseModel):
    """Request model for updating content relevance"""
    is_relevant: bool = Field(..., description="Whether the content is relevant")
    relevance_text: Optional[str] = Field(None, description="Updated relevance analysis text")
    relevance_score: Optional[str] = Field(None, ge=0.0, le=1.0, description="Relevance score (0.0 to 1.0)")
    confidence_score: Optional[str] = Field(None, ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0)")
    relevance_category: Optional[str] = Field(None, description="Relevance category")
    updated_by: Optional[str] = Field(None, description="User who updated the relevance")


def get_content_repository_controller():
    """Get content repository controller instance - lazy initialization"""
    return ContentRepositoryController()


def get_request_id(request: Request) -> str:
    """Get or generate request ID"""
    return getattr(request.state, 'request_id', str(uuid.uuid4())[:8])


@router.get("/", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def get_content_repository_entries(
        request: Request,
        project_id: Optional[str] = Query(None, description="Filter by project ID"),
        request_id_filter: Optional[str] = Query(None, alias="request_id", description="Filter by request ID"),
        limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of results (1-1000)")
):
    """
    Get content repository entries with optional filters
    
    - **project_id**: Filter by project ID (UUID)
    - **request_id**: Filter by request ID (UUID)
    - **limit**: Maximum number of results to return
    """
    try:
        controller = get_content_repository_controller()
        api_request_id = get_request_id(request)

        response = await controller.get_all_by_query(
            project_id=project_id,
            request_id=request_id_filter,
            limit=limit,
            api_request_id=api_request_id
        )

        return response

    except Exception as e:
        logger.error(f"Content repository query endpoint failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_response_detail("Failed to retrieve content repository entries", str(e))
        )


@router.put("/{content_id}/relevance", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def update_content_relevance(
        request: Request,
        content_id: str,
        request_data: UpdateRelevanceRequest
):
    """
    Update content relevance by content ID
    
    This endpoint allows users to update the relevance status and related fields
    for a specific content entry based on its content_id.
    
    - **content_id**: The UUID of the content entry
    - **is_relevant**: Whether the content is relevant (required)
    - **relevance_text**: Updated relevance analysis text (optional)
    - **relevance_score**: Relevance score between 0.0 and 1.0 (optional)
    - **confidence_score**: Confidence score between 0.0 and 1.0 (optional)
    - **relevance_category**: Relevance category (optional)
    - **updated_by**: User who updated the relevance (optional)
    """
    try:
        controller = get_content_repository_controller()
        api_request_id = get_request_id(request)

        response = await controller.update_relevance_by_content_id(
            content_id=content_id,
            is_relevant=request_data.is_relevant,
            relevance_text=request_data.relevance_text,
            relevance_score=request_data.relevance_score,
            confidence_score=request_data.confidence_score,
            relevance_category=request_data.relevance_category,
            updated_by=request_data.updated_by,
            api_request_id=api_request_id
        )

        return response

    except Exception as e:
        logger.error(f"Content relevance update endpoint failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_response_detail("Failed to update content relevance", str(e))
        )
