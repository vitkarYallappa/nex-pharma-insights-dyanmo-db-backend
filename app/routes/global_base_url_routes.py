"""
Global Base URL Routes
Clean and minimal API endpoints for global base URL operations
Follows the same pattern as ProjectRoutes for consistency
"""

from fastapi import APIRouter, Query, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uuid

from app.controllers.global_base_url_controller import GlobalBaseUrlController
from app.core.response import APIResponse, safe_response_detail
from app.core.logging import get_logger
from app.config.settings import settings

logger = get_logger("global_base_url_routes")
router = APIRouter()


def get_global_base_url_controller():
    """Get global base URL controller instance - lazy initialization"""
    return GlobalBaseUrlController()


def get_request_id(request: Request) -> str:
    """Get or generate request ID"""
    return getattr(request.state, 'request_id', str(uuid.uuid4())[:8])


class CreateGlobalBaseUrlRequest(BaseModel):
    """Request model for creating a global base URL"""
    url: str = Field(..., description="Base URL", min_length=1, max_length=2048)
    source_name: Optional[str] = Field(None, description="Source name", max_length=255)
    source_type: Optional[str] = Field(None, description="Source type", max_length=100)
    country_region: Optional[str] = Field(None, description="Country/region", max_length=100)
    is_active: bool = Field(True, description="Active status")
    url_metadata: Optional[Dict[str, Any]] = Field(None, description="URL metadata JSON")


# Global Base URL CRUD Operations
@router.post("/",
             response_model=APIResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Create global base URL",
             description="Create a new global base URL with metadata")
async def create_global_base_url(url_data: CreateGlobalBaseUrlRequest, request: Request) -> APIResponse:
    """Create a new global base URL"""
    request_id = get_request_id(request)
    logger.info(f"Create global base URL request: {url_data.url}")

    response = await get_global_base_url_controller().create_global_base_url(
        url=url_data.url,
        source_name=url_data.source_name,
        source_type=url_data.source_type,
        country_region=url_data.country_region,
        is_active=url_data.is_active,
        url_metadata=url_data.url_metadata,
        request_id=request_id
    )

    if response.status == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=safe_response_detail(response)
        )

    return response


@router.get("/{url_id}",
            response_model=APIResponse,
            summary="Get global base URL by ID",
            description="Retrieve global base URL information by URL ID")
async def get_global_base_url(url_id: str, request: Request) -> APIResponse:
    """Get global base URL by ID"""
    request_id = get_request_id(request)
    logger.info(f"Get global base URL request: {url_id}")

    response = await get_global_base_url_controller().get_global_base_url_by_id(url_id, request_id)

    if response.status == "error":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=safe_response_detail(response)
        )

    return response


@router.get("/",
            response_model=APIResponse,
            summary="Get global base URLs by query",
            description="Get list of global base URLs with optional filters")
async def get_global_base_urls_by_query(
        request: Request,
        source_name: Optional[str] = Query(None, description="Filter by source name"),
        source_type: Optional[str] = Query(None, description="Filter by source type"),
        country_region: Optional[str] = Query(None, description="Filter by country/region"),
        is_active: Optional[bool] = Query(None, description="Filter by active status"),
        limit: Optional[int] = Query(None, ge=1, le=settings.MAX_PAGE_SIZE,
                                     description="Maximum number of URLs to return")
) -> APIResponse:
    """Get global base URLs with optional filters"""
    request_id = get_request_id(request)
    logger.info("Get global base URLs by query request")

    response = await get_global_base_url_controller().get_all_global_base_url(
        source_name=source_name,
        source_type=source_type,
        country_region=country_region,
        is_active=is_active,
        limit=limit,
        request_id=request_id
    )

    return response
