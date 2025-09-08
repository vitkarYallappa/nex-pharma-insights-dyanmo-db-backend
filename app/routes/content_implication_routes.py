"""
Content Implication Routes
API endpoints for content implication operations
"""

from fastapi import APIRouter, Query, HTTPException, status, Request
from typing import Optional
from pydantic import BaseModel, Field
import uuid

from app.controllers.content_implication_controller import ContentImplicationController
from app.core.response import APIResponse, safe_response_detail
from app.core.logging import get_logger

logger = get_logger("content_implication_routes")
router = APIRouter()

def get_content_implication_controller():
    """Get content implication controller instance - lazy initialization"""
    return ContentImplicationController()

def get_request_id(request: Request) -> str:
    """Get or generate request ID"""
    return getattr(request.state, 'request_id', str(uuid.uuid4())[:8])

class RegenerateImplicationRequest(BaseModel):
    """Request model for regenerating an implication"""
    content_id: str = Field(..., description="Content ID (UUID as string)", min_length=1)
    metadata_field1: Optional[str] = Field(None, description="Additional metadata field 1", max_length=500)
    metadata_field2: Optional[str] = Field(None, description="Additional metadata field 2", max_length=500)
    metadata_field3: Optional[str] = Field(None, description="Additional metadata field 3", max_length=500)
    question_text: Optional[str] = Field(None, description="Optional question for QA generation", max_length=1000)

@router.get("/", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def get_content_implication_entries(
    request: Request,
    content_id: Optional[str] = Query(None, description="Filter by content ID"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of results (1-1000)")
):
    """
    Get content implication entries with optional filters
    - **content_id**: Filter by content ID (UUID)
    """
    try:
        controller = get_content_implication_controller()
        api_request_id = get_request_id(request)
        
        response = await controller.get_all_by_query(
            content_id=content_id,
            api_request_id=api_request_id
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Content implication query endpoint failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_response_detail("Failed to retrieve content implication entries", str(e))
        )

@router.post("/regenerate", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def regenerate_implication(
    request: Request,
    regenerate_request: RegenerateImplicationRequest
):
    """
    Regenerate implication for given content with version management
    
    - **content_id**: The content ID to regenerate implication for (UUID)
    - **metadata_field1**: Optional additional metadata field 1
    - **metadata_field2**: Optional additional metadata field 2
    - **metadata_field3**: Optional additional metadata field 3
    - **question_text**: Optional question text for QA generation
    """
    try:
        controller = get_content_implication_controller()
        api_request_id = get_request_id(request)
        
        response = await controller.regenerate_implication(
            content_id=regenerate_request.content_id,
            metadata_field1=regenerate_request.metadata_field1,
            metadata_field2=regenerate_request.metadata_field2,
            metadata_field3=regenerate_request.metadata_field3,
            question_text=regenerate_request.question_text,
            api_request_id=api_request_id
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Implication regeneration endpoint failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_response_detail("Failed to regenerate implication", str(e))
        )
