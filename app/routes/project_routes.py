"""
Project Routes
Clean and minimal API endpoints for project operations
Follows the same pattern as UserRoutes for consistency
"""

from fastapi import APIRouter, Query, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid

from app.controllers.project_controller import ProjectController
from app.core.response import APIResponse, safe_response_detail
from app.core.logging import get_logger
from app.config.settings import settings

logger = get_logger("project_routes")
router = APIRouter()

def get_project_controller():
    """Get project controller instance - lazy initialization"""
    return ProjectController()

def get_request_id(request: Request) -> str:
    """Get or generate request ID"""
    return getattr(request.state, 'request_id', str(uuid.uuid4())[:8])

class CreateProjectRequest(BaseModel):
    """Request model for creating a project"""
    name: str = Field(..., description="Project name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Project description", max_length=1000)
    created_by: str = Field(..., description="Creator user ID (UUID as string)")
    status: Optional[str] = Field("active", description="Project status")
    project_metadata: Optional[Dict[str, Any]] = Field(None, description="Project metadata JSON")
    module_config: Optional[Dict[str, Any]] = Field(None, description="Module configuration JSON")

class BaseUrlRequest(BaseModel):
    """Request model for base URL"""
    source_type: str = Field(..., description="Source type (e.g., government, academic, clinical)")
    source_name: str = Field(..., description="Source name (e.g., FDA, NIH)")
    url: str = Field(..., description="Base URL")
    country_region: Optional[str] = Field(None, description="Country or region")
    is_active: Optional[bool] = Field(True, description="Active status")
    url_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional URL metadata")

class TimeRangeRequest(BaseModel):
    """Request model for time range"""
    start: str = Field(..., description="Start date (YYYY-MM-DD)")
    end: str = Field(..., description="End date (YYYY-MM-DD)")
    date_range: Optional[str] = Field(None, description="Human readable date range")

class CreateProjectRequestWithDetails(BaseModel):
    """Request model for creating a complete project request with all related entities"""
    project_id: Optional[str] = Field(None, description="Optional existing project ID")
    title: str = Field(..., description="Project request title", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Project request description", max_length=2000)
    time_range: Optional[TimeRangeRequest] = Field(None, description="Time range for the request")
    priority: Optional[str] = Field("medium", description="Priority level (low, medium, high)")
    created_by: str = Field(..., description="Creator user ID (UUID as string)")
    keywords: List[str] = Field(default=[], description="List of keywords for the request")
    base_urls: List[BaseUrlRequest] = Field(default=[], description="List of base URLs for monitoring")

# Project CRUD Operations
# @router.post("/",
#             response_model=APIResponse,
#             status_code=status.HTTP_201_CREATED,
#             summary="Create project",
#             description="Create a new project with metadata and configuration")
# async def create_project(project_data: CreateProjectRequest, request: Request) -> APIResponse:
#     """Create a new project"""
#     request_id = get_request_id(request)
#     logger.info(f"Create project request: {project_data.name}")
#
#     response = await get_project_controller().create_project(
#         name=project_data.name,
#         created_by=project_data.created_by,
#         description=project_data.description,
#         status=project_data.status,
#         project_metadata=project_data.project_metadata,
#         module_config=project_data.module_config,
#         request_id=request_id
#     )
#
#     if response.status == "error":
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=safe_response_detail(response)
#         )
#
#     return response

@router.get("/",
           response_model=APIResponse,
           summary="Get projects by query",
           description="Get list of projects with optional filters")
async def get_projects_by_query(
    request: Request,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by project status"),
    created_by: Optional[str] = Query(None, description="Filter by creator user ID"),
    limit: Optional[int] = Query(None, ge=1, le=settings.MAX_PAGE_SIZE, 
                                description="Maximum number of projects to return")
) -> APIResponse:
    """Get projects with optional filters"""
    request_id = get_request_id(request)
    logger.info("Get projects by query request")
    
    response = await get_project_controller().get_projects_by_query(
        status=status_filter,
        created_by=created_by,
        limit=limit,
        request_id=request_id
    )
    
    return response

# Project Recent Feeds API
@router.get("/recent-feeds",
           response_model=APIResponse,
           summary="Get recent content feeds",
           description="Get recent content summary data with insights and implications count for latest projects")
async def get_recent_content_feeds(request: Request) -> APIResponse:
    """Get recent content feeds with insights and implications count"""
    request_id = get_request_id(request)
    logger.info("Get recent content feeds request")
    
    response = await get_project_controller().get_recent_content_feeds(request_id)
    
    if response.status == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_response_detail(response)
        )
    
    return response

# Dashboard Statistics APIs
@router.get("/statistics/dashboard",
           response_model=APIResponse,
           summary="Get dashboard statistics",
           description="Get comprehensive dashboard statistics including project count, global keywords, URLs, insights, and implications")
async def get_dashboard_statistics(request: Request) -> APIResponse:
    """Get comprehensive dashboard statistics for reporting"""
    request_id = get_request_id(request)
    logger.info("Get dashboard statistics request")
    
    response = await get_project_controller().get_dashboard_statistics(request_id)
    
    if response.status == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_response_detail(response)
        )
    
    return response

@router.get("/statistics/project-breakdown",
           response_model=APIResponse,
           summary="Get project breakdown statistics",
           description="Get detailed project breakdown statistics with per-project insights and implications count")
async def get_project_breakdown_statistics(
    request: Request,
    limit: Optional[int] = Query(None, ge=1, le=settings.MAX_PAGE_SIZE, 
                                description="Maximum number of projects to include")
) -> APIResponse:
    """Get detailed project breakdown statistics"""
    request_id = get_request_id(request)
    logger.info("Get project breakdown statistics request")
    
    response = await get_project_controller().get_project_breakdown_statistics(limit, request_id)
    
    if response.status == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_response_detail(response)
        )
    
    return response

@router.get("/statistics/global-resources",
           response_model=APIResponse,
           summary="Get global resources statistics",
           description="Get detailed statistics about global resources (keywords and URLs)")
async def get_global_resources_statistics(request: Request) -> APIResponse:
    """Get global resources statistics (keywords and URLs)"""
    request_id = get_request_id(request)
    logger.info("Get global resources statistics request")
    
    response = await get_project_controller().get_global_resources_statistics(request_id)
    
    if response.status == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_response_detail(response)
        )
    
    return response

@router.get("/{project_id}",
           response_model=APIResponse,
           summary="Get project by ID",
           description="Retrieve project information by project ID")
async def get_project(project_id: str, request: Request) -> APIResponse:
    """Get project by ID"""
    request_id = get_request_id(request)
    logger.info(f"Get project request: {project_id}")
    
    response = await get_project_controller().get_project_by_id(project_id, request_id)
    
    if response.status == "error":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=safe_response_detail(response)
        )
    
    return response

# Project Request Creation Orchestrator
@router.post("/request",
            response_model=APIResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Create complete project request",
            description="Create a complete project request with project, request, keywords, and source URLs")
async def create_project_request_with_details(
    request_data: CreateProjectRequestWithDetails, 
    request: Request
) -> APIResponse:
    """Create a complete project request with all related entities"""
    request_id = get_request_id(request)
    logger.info(f"[{request_id}] Create project request orchestration: {request_data.title}")
    
    # Convert Pydantic models to dictionaries
    payload = {
        "project_id": request_data.project_id,
        "title": request_data.title,
        "description": request_data.description,
        "time_range": request_data.time_range.model_dump() if request_data.time_range else {},
        "priority": request_data.priority,
        "created_by": request_data.created_by,
        "keywords": request_data.keywords,
        "base_urls": [url.model_dump() for url in request_data.base_urls]
    }
    
    # Call controller method (proper layered architecture)
    response = await get_project_controller().create_project_request_with_details(payload, request_id)
    
    if response.status == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=safe_response_detail(response)
        )
    
    return response 