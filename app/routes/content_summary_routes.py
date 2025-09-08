"""
Content Summary Routes
API endpoints for content summary operations
"""

from fastapi import APIRouter, Query, HTTPException, status, Request
from typing import Optional
import uuid

from app.controllers.content_summary_controller import ContentSummaryController
from app.core.response import APIResponse, safe_response_detail
from app.core.logging import get_logger

logger = get_logger("content_summary_routes")
router = APIRouter()


def get_content_summary_controller():
    """Get content summary controller instance - lazy initialization"""
    return ContentSummaryController()


def get_request_id(request: Request) -> str:
    """Get or generate request ID"""
    return getattr(request.state, 'request_id', str(uuid.uuid4())[:8])


@router.get("/", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def get_content_summary_entries(
        request: Request,
        content_id: Optional[str] = Query(None, description="Filter by content ID"),
        limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of results (1-1000)")
):
    """
    Get content summary entries with optional filters
    
    - **content_id**: Filter by content ID (UUID)
    - **limit**: Maximum number of results to return
    """
    try:
        controller = get_content_summary_controller()
        api_request_id = get_request_id(request)

        response = await controller.get_all_by_query(
            content_id=content_id,
            limit=limit,
            api_request_id=api_request_id
        )

        return response

    except Exception as e:
        logger.error(f"Content summary query endpoint failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_response_detail("Failed to retrieve content summary entries", str(e))
        )
