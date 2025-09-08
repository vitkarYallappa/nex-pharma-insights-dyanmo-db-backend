"""
Insight Comment Routes
API endpoints for insight comment operations
"""

from fastapi import APIRouter, Query, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Optional
import uuid

from app.controllers.insight_comment_controller import InsightCommentController
from app.core.response import APIResponse, safe_response_detail
from app.core.logging import get_logger

logger = get_logger("insight_comment_routes")
router = APIRouter()

def get_insight_comment_controller():
    """Get insight comment controller instance - lazy initialization"""
    return InsightCommentController()

def get_request_id(request: Request) -> str:
    """Get or generate request ID"""
    return getattr(request.state, 'request_id', str(uuid.uuid4())[:8])

class CreateInsightCommentRequest(BaseModel):
    """Request model for creating an insight comment"""
    insight_id: str = Field(..., description="Insight ID (UUID as string)", min_length=1)
    comment_text: str = Field(..., description="Comment text", min_length=1, max_length=5000)
    comment_type: Optional[str] = Field(None, description="Comment type", max_length=100)

@router.get("/", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def get_insight_comment_entries(
    request: Request,
    insight_id: Optional[str] = Query(None, description="Filter by insight ID"),
    comment_type: Optional[str] = Query(None, description="Filter by comment type"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of results (1-1000)")
):
    """
    Get insight comment entries with optional filters
    
    - **insight_id**: Filter by insight ID (UUID)
    - **comment_type**: Filter by comment type
    - **limit**: Maximum number of results to return
    """
    try:
        controller = get_insight_comment_controller()
        api_request_id = get_request_id(request)
        
        response = await controller.get_all_by_query(
            insight_id=insight_id,
            comment_type=comment_type,
            limit=limit,
            api_request_id=api_request_id
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Insight comment query endpoint failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_response_detail("Failed to retrieve insight comment entries", str(e))
        )

@router.post("/", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_insight_comment(
    request: Request,
    comment_request: CreateInsightCommentRequest
):
    """
    Create a new insight comment
    
    - **insight_id**: The insight ID to comment on (UUID)
    - **comment_text**: The comment text content
    - **comment_type**: Optional comment type/category
    """
    try:
        controller = get_insight_comment_controller()
        api_request_id = get_request_id(request)
        
        response = await controller.create_insight_comment(
            insight_id=comment_request.insight_id,
            comment_text=comment_request.comment_text,
            comment_type=comment_request.comment_type,
            api_request_id=api_request_id
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Insight comment creation endpoint failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_response_detail("Failed to create insight comment", str(e))
        )
