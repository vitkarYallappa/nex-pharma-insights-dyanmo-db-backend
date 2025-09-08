"""
Content Repository Routes
API endpoints for content repository operations
"""

from fastapi import APIRouter, Query, HTTPException, status, Request
from typing import Optional
import uuid

from app.controllers.content_repository_controller import ContentRepositoryController
from app.core.response import APIResponse, safe_response_detail
from app.core.logging import get_logger

logger = get_logger("content_repository_routes")
router = APIRouter()


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
