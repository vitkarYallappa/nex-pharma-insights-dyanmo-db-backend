"""
Global Keywords Routes
Clean and minimal API endpoints for global keywords operations
Follows the same pattern as ProjectRoutes for consistency
"""

from fastapi import APIRouter, Query, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uuid

from app.controllers.global_keywords_controller import GlobalKeywordsController
from app.core.response import APIResponse, safe_response_detail
from app.core.logging import get_logger
from app.config.settings import settings

logger = get_logger("global_keywords_routes")
router = APIRouter()

def get_global_keywords_controller():
    """Get global keywords controller instance - lazy initialization"""
    return GlobalKeywordsController()

def get_request_id(request: Request) -> str:
    """Get or generate request ID"""
    return getattr(request.state, 'request_id', str(uuid.uuid4())[:8])

class CreateGlobalKeywordRequest(BaseModel):
    """Request model for creating a global keyword"""
    keyword: str = Field(..., description="Keyword text", min_length=1, max_length=255)
    keyword_type: Optional[str] = Field(None, description="Keyword type/category", max_length=100)

# Global Keywords CRUD Operations
@router.post("/",
            response_model=APIResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Create global keyword",
            description="Create a new global keyword with optional type")
async def create_global_keyword(keyword_data: CreateGlobalKeywordRequest, request: Request) -> APIResponse:
    """Create a new global keyword"""
    request_id = get_request_id(request)
    logger.info(f"Create global keyword request: {keyword_data.keyword}")
    
    response = await get_global_keywords_controller().create_global_keyword(
        keyword=keyword_data.keyword,
        keyword_type=keyword_data.keyword_type,
        request_id=request_id
    )
    
    if response.status == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=safe_response_detail(response)
        )
    
    return response

@router.get("/",
           response_model=APIResponse,
           summary="Get global keywords by query",
           description="Get list of global keywords with optional filters")
async def get_global_keywords_by_query(
    request: Request,
    keyword_type: Optional[str] = Query(None, description="Filter by keyword type"),
    limit: Optional[int] = Query(None, ge=1, le=settings.MAX_PAGE_SIZE, 
                                description="Maximum number of keywords to return")
) -> APIResponse:
    """Get global keywords with optional filters"""
    request_id = get_request_id(request)
    logger.info("Get global keywords by query request")
    
    response = await get_global_keywords_controller().get_global_keywords_by_query(
        keyword_type=keyword_type,
        limit=limit,
        request_id=request_id
    )
    
    return response

@router.get("/all",
           response_model=APIResponse,
           summary="Get all global keywords by query",
           description="Get all global keywords with optional filters (alias endpoint)")
async def get_all_global_keywords_by_query(
    request: Request,
    keyword_type: Optional[str] = Query(None, description="Filter by keyword type"),
    limit: Optional[int] = Query(None, ge=1, le=settings.MAX_PAGE_SIZE, 
                                description="Maximum number of keywords to return")
) -> APIResponse:
    """Get all global keywords with optional filters (alias for get_global_keywords_by_query)"""
    request_id = get_request_id(request)
    logger.info("Get all global keywords by query request")
    
    response = await get_global_keywords_controller().get_all_global_keywords_by_query(
        keyword_type=keyword_type,
        limit=limit,
        request_id=request_id
    )
    
    return response 