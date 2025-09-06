"""
Seeder Routes
API endpoints for database seeding operations
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Dict, Any, List, Optional

from app.controllers.seeder_controller import SeederController
from app.core.response import APIResponse

# Create router
router = APIRouter(prefix="/seeders", tags=["seeders"])

# Initialize controller
seeder_controller = SeederController()

@router.post("/run", response_model=Dict[str, Any])
async def run_seeders(
    seeder_names: Optional[List[str]] = Query(
        None, 
        description="Optional list of specific seeders to run. If not provided, runs all seeders."
    )
):
    """
    Run database seeders to populate data
    
    Executes seeder files to populate the database with initial or test data.
    Seeders are run in dependency order to ensure data consistency.
    
    Args:
        seeder_names: Optional list of specific seeders to run (e.g., ["user_seeder", "product_seeder"])
    
    Returns:
        Dict[str, Any]: Success/failure status with seeding details
    
    Raises:
        HTTPException: If seeding operation fails
    
    Examples:
        - Run all seeders: POST /seeders/run
        - Run specific seeders: POST /seeders/run?seeder_names=user_seeder&seeder_names=product_seeder
    """
    response = await seeder_controller.run_seeders(seeder_names)
    return response.model_dump() if hasattr(response, 'model_dump') else (response.dict() if hasattr(response, 'dict') else response.__dict__)

@router.post("/clear", response_model=Dict[str, Any])
async def clear_seeders(
    seeder_names: Optional[List[str]] = Query(
        None,
        description="Optional list of specific seeders to clear. If not provided, clears all seeders."
    )
):
    """
    Clear seeded data from database
    
    Removes data that was inserted by seeders. This is useful for cleaning up
    test data or resetting the database to a clean state.
    
    Args:
        seeder_names: Optional list of specific seeders to clear (e.g., ["user_seeder"])
    
    Returns:
        Dict[str, Any]: Success/failure status with clearing details
    
    Raises:
        HTTPException: If clearing operation fails
    
    Examples:
        - Clear all seeded data: POST /seeders/clear
        - Clear specific seeders: POST /seeders/clear?seeder_names=user_seeder
    """
    response = await seeder_controller.clear_seeders(seeder_names)
    return response.model_dump() if hasattr(response, 'model_dump') else (response.dict() if hasattr(response, 'dict') else response.__dict__)

@router.get("/status", response_model=Dict[str, Any])
async def get_seeder_status():
    """
    Get current seeder status
    
    Shows which seeders are available, their descriptions, dependencies,
    and current status. Useful for checking what seeders exist before running them.
    
    Returns:
        Dict[str, Any]: List of available seeders with their details
    
    Raises:
        HTTPException: If status check fails
    """
    response = await seeder_controller.get_seeder_status()
    return response.model_dump() if hasattr(response, 'model_dump') else (response.dict() if hasattr(response, 'dict') else response.__dict__) 