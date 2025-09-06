"""
Seeder Controller
Handles database seeding operations via API endpoints
"""

from fastapi import HTTPException, status
from typing import Dict, Any, List, Optional
import asyncio
import traceback
from pathlib import Path
import importlib.util
import sys
import os

from app.core.logging import get_logger
from app.core.response import APIResponse, ResponseFormatter
from app.config.settings import settings

logger = get_logger("seeder_controller")

class SeederController:
    """Controller for handling database seeding operations"""
    
    def __init__(self):
        self.seeders_dir = Path(__file__).parent.parent.parent / "seeders"
        
    async def run_seeders(self, seeder_names: Optional[List[str]] = None) -> APIResponse:
        """
        Run database seeders to populate data
        
        Args:
            seeder_names: Optional list of specific seeders to run. If None, runs all seeders.
        """
        try:
            logger.info("Starting seeder run operation")
            
            # Get seeder files
            if seeder_names:
                seeder_files = self._get_specific_seeders(seeder_names)
            else:
                seeder_files = self._get_all_seeders()
            
            if not seeder_files:
                return ResponseFormatter.success(
                    message="No seeders found to run",
                    data={"seeders_run": 0, "status": "no_seeders"}
                )
            
            # Sort seeders by dependencies
            sorted_seeders = self._sort_seeders_by_dependencies(seeder_files)
            
            results = []
            successful_seeders = 0
            
            for seeder_file in sorted_seeders:
                try:
                    logger.info(f"Running seeder: {seeder_file.name}")
                    
                    # Import and execute seeder
                    seeder_class = self._import_seeder(seeder_file)
                    seeder_instance = seeder_class()
                    
                    # Run the seed method
                    success = await seeder_instance.seed()
                    
                    if success:
                        results.append({
                            "seeder": seeder_instance.name,
                            "file": seeder_file.name,
                            "status": "success",
                            "description": seeder_instance.description
                        })
                        successful_seeders += 1
                        logger.info(f"Successfully ran seeder: {seeder_instance.name}")
                    else:
                        results.append({
                            "seeder": seeder_instance.name,
                            "file": seeder_file.name,
                            "status": "failed",
                            "error": "Seeder returned False"
                        })
                        logger.error(f"Seeder {seeder_instance.name} returned False")
                    
                except Exception as e:
                    error_msg = f"Failed to run seeder {seeder_file.name}: {str(e)}"
                    logger.error(error_msg)
                    logger.error(traceback.format_exc())
                    
                    results.append({
                        "seeder": seeder_file.name,
                        "file": seeder_file.name,
                        "status": "failed",
                        "error": str(e)
                    })
            
            if successful_seeders == len(sorted_seeders):
                return ResponseFormatter.success(
                    message=f"Successfully ran {successful_seeders} seeders",
                    data={
                        "seeders_run": successful_seeders,
                        "total_seeders": len(sorted_seeders),
                        "status": "completed",
                        "results": results,
                        "environment": settings.TABLE_ENVIRONMENT
                    }
                )
            else:
                return ResponseFormatter.error(
                    message=f"Seeding partially failed. {successful_seeders}/{len(sorted_seeders)} completed",
                    data={
                        "seeders_run": successful_seeders,
                        "total_seeders": len(sorted_seeders),
                        "status": "partial",
                        "results": results,
                        "environment": settings.TABLE_ENVIRONMENT
                    },
                    status_code=status.HTTP_207_MULTI_STATUS
                )
                
        except Exception as e:
            logger.error(f"Seeder run operation failed: {str(e)}")
            logger.error(traceback.format_exc())
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Seeder operation failed: {str(e)}"
            )
    
    async def clear_seeders(self, seeder_names: Optional[List[str]] = None) -> APIResponse:
        """
        Clear seeded data from database
        
        Args:
            seeder_names: Optional list of specific seeders to clear. If None, clears all seeders.
        """
        try:
            logger.info("Starting seeder clear operation")
            
            # Get seeder files
            if seeder_names:
                seeder_files = self._get_specific_seeders(seeder_names)
            else:
                seeder_files = self._get_all_seeders()
            
            if not seeder_files:
                return ResponseFormatter.success(
                    message="No seeders found to clear",
                    data={"seeders_cleared": 0, "status": "no_seeders"}
                )
            
            # Sort seeders in reverse dependency order for clearing
            sorted_seeders = self._sort_seeders_by_dependencies(seeder_files, reverse=True)
            
            results = []
            successful_clears = 0
            
            for seeder_file in sorted_seeders:
                try:
                    logger.info(f"Clearing seeder: {seeder_file.name}")
                    
                    # Import and execute seeder clear
                    seeder_class = self._import_seeder(seeder_file)
                    seeder_instance = seeder_class()
                    
                    # Run the clear method
                    success = await seeder_instance.clear()
                    
                    if success:
                        results.append({
                            "seeder": seeder_instance.name,
                            "file": seeder_file.name,
                            "status": "success",
                            "description": seeder_instance.description
                        })
                        successful_clears += 1
                        logger.info(f"Successfully cleared seeder: {seeder_instance.name}")
                    else:
                        results.append({
                            "seeder": seeder_instance.name,
                            "file": seeder_file.name,
                            "status": "failed",
                            "error": "Seeder clear returned False"
                        })
                        logger.error(f"Seeder clear {seeder_instance.name} returned False")
                    
                except Exception as e:
                    error_msg = f"Failed to clear seeder {seeder_file.name}: {str(e)}"
                    logger.error(error_msg)
                    logger.error(traceback.format_exc())
                    
                    results.append({
                        "seeder": seeder_file.name,
                        "file": seeder_file.name,
                        "status": "failed",
                        "error": str(e)
                    })
                    
                    # Continue with other clears even if one fails
                    continue
            
            return ResponseFormatter.success(
                message=f"Clear completed. {successful_clears}/{len(sorted_seeders)} seeders cleared",
                data={
                    "seeders_cleared": successful_clears,
                    "total_seeders": len(sorted_seeders),
                    "status": "completed" if successful_clears == len(sorted_seeders) else "partial",
                    "results": results,
                    "environment": settings.TABLE_ENVIRONMENT
                }
            )
                
        except Exception as e:
            logger.error(f"Seeder clear operation failed: {str(e)}")
            logger.error(traceback.format_exc())
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Seeder clear failed: {str(e)}"
            )
    
    async def get_seeder_status(self) -> APIResponse:
        """
        Get current seeder status
        Shows which seeders are available and their information
        """
        try:
            seeder_files = self._get_all_seeders()
            
            seeders_info = []
            for seeder_file in seeder_files:
                try:
                    seeder_class = self._import_seeder(seeder_file)
                    seeder_instance = seeder_class()
                    
                    seeders_info.append({
                        "name": seeder_instance.name,
                        "file": seeder_file.name,
                        "description": seeder_instance.description,
                        "dependencies": seeder_instance.dependencies,
                        "created_at": seeder_file.stat().st_mtime,
                        "status": "available"
                    })
                except Exception as e:
                    seeders_info.append({
                        "name": seeder_file.stem,
                        "file": seeder_file.name,
                        "description": "Failed to load",
                        "error": str(e),
                        "status": "error"
                    })
            
            return ResponseFormatter.success(
                message=f"Found {len(seeders_info)} seeders",
                data={
                    "total_seeders": len(seeders_info),
                    "seeders": seeders_info,
                    "environment": settings.TABLE_ENVIRONMENT
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get seeder status: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get seeder status: {str(e)}"
            )
    
    def _get_all_seeders(self) -> List[Path]:
        """Get all seeder files"""
        if not self.seeders_dir.exists():
            logger.warning(f"Seeders directory not found: {self.seeders_dir}")
            return []
        
        seeder_files = []
        for file_path in self.seeders_dir.glob("*_seeder.py"):
            if file_path.name not in ["base_seeder.py", "__init__.py"]:
                seeder_files.append(file_path)
        
        return seeder_files
    
    def _get_specific_seeders(self, seeder_names: List[str]) -> List[Path]:
        """Get specific seeder files by name"""
        all_seeders = self._get_all_seeders()
        specific_seeders = []
        
        for seeder_name in seeder_names:
            # Try to find seeder by name (with or without _seeder.py suffix)
            seeder_file = None
            
            for file_path in all_seeders:
                if (file_path.stem == seeder_name or 
                    file_path.stem == f"{seeder_name}_seeder" or
                    file_path.name == seeder_name):
                    seeder_file = file_path
                    break
            
            if seeder_file:
                specific_seeders.append(seeder_file)
            else:
                logger.warning(f"Seeder not found: {seeder_name}")
        
        return specific_seeders
    
    def _sort_seeders_by_dependencies(self, seeder_files: List[Path], reverse: bool = False) -> List[Path]:
        """Sort seeders by their dependencies"""
        # For now, just return the files as-is
        # In a more complex system, you would implement topological sorting
        # based on the dependencies property of each seeder
        
        sorted_files = sorted(seeder_files, key=lambda x: x.name)
        if reverse:
            sorted_files.reverse()
        
        return sorted_files
    
    def _import_seeder(self, seeder_file: Path):
        """Import a seeder class from file"""
        spec = importlib.util.spec_from_file_location(
            seeder_file.stem, 
            seeder_file
        )
        
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load seeder from {seeder_file}")
        
        module = importlib.util.module_from_spec(spec)
        
        # Add to sys.modules to handle relative imports
        sys.modules[seeder_file.stem] = module
        
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            # Clean up sys.modules on failure
            if seeder_file.stem in sys.modules:
                del sys.modules[seeder_file.stem]
            raise e
        
        # Find the seeder class (should end with 'Seeder')
        seeder_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                attr_name.endswith('Seeder') and 
                attr_name != 'BaseSeeder'):
                seeder_class = attr
                break
        
        if seeder_class is None:
            raise ImportError(f"No seeder class found in {seeder_file}")
        
        return seeder_class 