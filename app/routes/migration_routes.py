"""
Migration Routes
API endpoints for database migration operations
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from app.controllers.migration_controller import MigrationController
from app.core.response import APIResponse

# Create router
router = APIRouter(prefix="/migrations", tags=["migrations"])

# Initialize controller
migration_controller = MigrationController()

@router.post("/run", response_model=Dict[str, Any])
async def run_migrations():
    """
    Run all pending migrations (migrate:up)
    
    Creates tables and applies schema changes to the database.
    This endpoint will execute all migration files in chronological order.
    
    Returns:
        Dict[str, Any]: Success/failure status with migration details
    
    Raises:
        HTTPException: If migration operation fails
    """
    response = await migration_controller.run_migrations()
    return response.model_dump() if hasattr(response, 'model_dump') else (response.dict() if hasattr(response, 'dict') else response.__dict__)

@router.post("/rollback", response_model=Dict[str, Any])
async def rollback_migrations():
    """
    Rollback all migrations (migrate:down)
    
    Deletes tables and reverts schema changes from the database.
    This endpoint will execute rollback operations in reverse chronological order.
    
    Returns:
        Dict[str, Any]: Success/failure status with rollback details
    
    Raises:
        HTTPException: If rollback operation fails
    """
    response = await migration_controller.rollback_migrations()
    return response.model_dump() if hasattr(response, 'model_dump') else (response.dict() if hasattr(response, 'dict') else response.__dict__)

@router.get("/status", response_model=Dict[str, Any])
async def get_migration_status():
    """
    Get current migration status
    
    Shows which migrations are available, their descriptions, and current status.
    Useful for checking what migrations exist before running them.
    
    Returns:
        Dict[str, Any]: List of available migrations with their details
    
    Raises:
        HTTPException: If status check fails
    """
    response = await migration_controller.get_migration_status()
    return response.model_dump() if hasattr(response, 'model_dump') else (response.dict() if hasattr(response, 'dict') else response.__dict__) 