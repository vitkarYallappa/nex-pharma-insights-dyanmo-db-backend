"""
Simplified User Routes
Clean and minimal API endpoints for user operations
"""

from fastapi import APIRouter, Query, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

from app.controllers.user_controller import UserController
from app.core.response import APIResponse
from app.core.logging import get_logger
from app.config.settings import settings

logger = get_logger("user_routes")
router = APIRouter()

def get_user_controller():
    """Get user controller instance - lazy initialization"""
    return UserController()

def get_request_id(request: Request) -> str:
    """Get or generate request ID"""
    return getattr(request.state, 'request_id', str(uuid.uuid4())[:8])

class CreateUserRequest(BaseModel):
    """Request model for creating a user"""
    email: EmailStr
    name: str
    password: str
    is_active: bool = True
    role: str = "user"

# User CRUD Operations
@router.post("/",
            response_model=APIResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Create user",
            description="Create a new user account")
async def create_user(user_data: CreateUserRequest, request: Request) -> APIResponse:
    """Create a new user"""
    request_id = get_request_id(request)
    logger.info(f"Create user request: {user_data.email}")
    
    response = await get_user_controller().create_user(
        email=user_data.email,
        name=user_data.name,
        password=user_data.password,
        is_active=user_data.is_active,
        role=user_data.role,
        request_id=request_id
    )
    
    if response.status == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.model_dump() if hasattr(response, 'model_dump') else response.dict()
        )
    
    return response

@router.get("/{user_id}",
           response_model=APIResponse,
           summary="Get user by ID",
           description="Retrieve user information by user ID")
async def get_user(user_id: str, request: Request) -> APIResponse:
    """Get user by ID"""
    request_id = get_request_id(request)
    logger.info(f"Get user request: {user_id}")
    
    response = await get_user_controller().get_user_by_id(user_id, request_id)
    
    if response.status == "error":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=response.model_dump() if hasattr(response, 'model_dump') else response.dict()
        )
    
    return response

@router.get("/email/{email}",
           response_model=APIResponse,
           summary="Get user by email",
           description="Retrieve user information by email")
async def get_user_by_email(email: str, request: Request) -> APIResponse:
    """Get user by email"""
    request_id = get_request_id(request)
    logger.info(f"Get user by email: {email}")
    
    response = await get_user_controller().get_user_by_email(email, request_id)
    
    if response.status == "error":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=response.model_dump() if hasattr(response, 'model_dump') else response.dict()
        )
    
    return response

@router.get("/",
           response_model=APIResponse,
           summary="List users",
           description="Get list of users with optional filters")
async def list_users(
    request: Request,
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    role: Optional[str] = Query(None, description="Filter by role"),
    limit: Optional[int] = Query(None, ge=1, le=settings.MAX_PAGE_SIZE, 
                                description="Maximum number of users to return")
) -> APIResponse:
    """List users with optional filters"""
    request_id = get_request_id(request)
    logger.info("List users request")
    
    response = await get_user_controller().list_users(
        is_active=is_active,
        role=role,
        limit=limit,
        request_id=request_id
    )
    
    return response