"""
Project Routes
Clean and minimal API endpoints for project operations
Follows the same pattern as UserRoutes for consistency
"""

from fastapi import APIRouter, Query, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uuid

from app.controllers.project_controller import ProjectController
from app.core.response import APIResponse
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

# Project CRUD Operations
@router.post("/",
            response_model=APIResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Create project",
            description="Create a new project with metadata and configuration")
async def create_project(project_data: CreateProjectRequest, request: Request) -> APIResponse:
    """Create a new project"""
    request_id = get_request_id(request)
    logger.info(f"Create project request: {project_data.name}")
    
    response = await get_project_controller().create_project(
        name=project_data.name,
        created_by=project_data.created_by,
        description=project_data.description,
        status=project_data.status,
        project_metadata=project_data.project_metadata,
        module_config=project_data.module_config,
        request_id=request_id
    )
    
    if response.status == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.model_dump() if hasattr(response, 'model_dump') else response.dict()
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
            detail=response.model_dump() if hasattr(response, 'model_dump') else response.dict()
        )
    
    return response

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