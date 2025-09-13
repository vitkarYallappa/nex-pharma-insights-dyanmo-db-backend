"""
Migration Controller
Handles database migration operations via API endpoints
"""

from fastapi import HTTPException, status
from typing import Dict, Any, List
import asyncio
import traceback
from pathlib import Path
import importlib.util
import sys
import os

from app.core.logging import get_logger
from app.core.response import APIResponse, ResponseFormatter
from app.config.settings import settings

logger = get_logger("migration_controller")

class MigrationController:
    """Controller for handling database migration operations"""
    
    def __init__(self):
        self.migrations_dir = Path(__file__).parent.parent.parent / "migrations"
        
    async def run_migrations(self) -> APIResponse:
        """
        Run all pending migrations (migrate:up)
        Creates tables and applies schema changes
        """
        try:
            logger.info("Starting migration run operation")
            
            # Get all migration files
            migration_files = self._get_migration_files()
            
            if not migration_files:
                return ResponseFormatter.success(
                    message="No migrations found to run",
                    data={"migrations_run": 0, "status": "up_to_date"}
                )
            
            results = []
            successful_migrations = 0
            
            for migration_file in migration_files:
                try:
                    logger.info(f"Running migration: {migration_file.name}")
                    
                    # Import and execute migration
                    migration_class = self._import_migration(migration_file)
                    migration_instance = migration_class()
                    
                    # Run the up method
                    await migration_instance.up()
                    
                    results.append({
                        "migration": migration_file.name,
                        "status": "success",
                        "description": migration_instance.description
                    })
                    successful_migrations += 1
                    
                    logger.info(f"Successfully ran migration: {migration_file.name}")
                    
                except Exception as e:
                    error_msg = f"Failed to run migration {migration_file.name}: {str(e)}"
                    logger.error(error_msg)
                    logger.error(traceback.format_exc())
                    
                    results.append({
                        "migration": migration_file.name,
                        "status": "failed",
                        "error": str(e)
                    })
                    
                    # Stop on first failure to maintain consistency
                    break
            
            if successful_migrations == len(migration_files):
                return ResponseFormatter.success(
                    message=f"Successfully ran {successful_migrations} migrations",
                    data={
                        "migrations_run": successful_migrations,
                        "total_migrations": len(migration_files),
                        "status": "completed",
                        "results": results
                    }
                )
            else:
                # Create custom error response with data
                from app.core.response import APIResponse, ResponseStatus
                from datetime import datetime
                return APIResponse(
                    status=ResponseStatus.ERROR,
                    message=f"Migration failed. {successful_migrations}/{len(migration_files)} completed",
                    data={
                        "migrations_run": successful_migrations,
                        "total_migrations": len(migration_files),
                        "status": "failed",
                        "results": results
                    },
                    timestamp=datetime.utcnow()
                )
                
        except Exception as e:
            logger.error(f"Migration run operation failed: {str(e)}")
            logger.error(traceback.format_exc())
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Migration operation failed: {str(e)}"
            )
    
    async def rollback_migrations(self) -> APIResponse:
        """
        Rollback all migrations (migrate:down)
        Deletes tables and reverts schema changes
        """
        try:
            logger.info("Starting migration rollback operation")
            
            # Get all migration files in reverse order
            migration_files = self._get_migration_files(reverse=True)
            
            if not migration_files:
                return ResponseFormatter.success(
                    message="No migrations found to rollback",
                    data={"migrations_rolled_back": 0, "status": "clean"}
                )
            
            results = []
            successful_rollbacks = 0
            
            for migration_file in migration_files:
                try:
                    logger.info(f"Rolling back migration: {migration_file.name}")
                    
                    # Import and execute migration rollback
                    migration_class = self._import_migration(migration_file)
                    migration_instance = migration_class()
                    
                    # Run the down method
                    await migration_instance.down()
                    
                    results.append({
                        "migration": migration_file.name,
                        "status": "success",
                        "description": migration_instance.description
                    })
                    successful_rollbacks += 1
                    
                    logger.info(f"Successfully rolled back migration: {migration_file.name}")
                    
                except Exception as e:
                    error_msg = f"Failed to rollback migration {migration_file.name}: {str(e)}"
                    logger.error(error_msg)
                    logger.error(traceback.format_exc())
                    
                    results.append({
                        "migration": migration_file.name,
                        "status": "failed",
                        "error": str(e)
                    })
                    
                    # Continue with other rollbacks even if one fails
                    continue
            
            return ResponseFormatter.success(
                message=f"Rollback completed. {successful_rollbacks}/{len(migration_files)} migrations rolled back",
                data={
                    "migrations_rolled_back": successful_rollbacks,
                    "total_migrations": len(migration_files),
                    "status": "completed" if successful_rollbacks == len(migration_files) else "partial",
                    "results": results
                }
            )
                
        except Exception as e:
            logger.error(f"Migration rollback operation failed: {str(e)}")
            logger.error(traceback.format_exc())
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Migration rollback failed: {str(e)}"
            )
    
    async def get_migration_status(self) -> APIResponse:
        """
        Get current migration status
        Shows which migrations are available and their status
        """
        try:
            migration_files = self._get_migration_files()
            
            migrations_info = []
            for migration_file in migration_files:
                try:
                    migration_class = self._import_migration(migration_file)
                    migration_instance = migration_class()
                    
                    migrations_info.append({
                        "file": migration_file.name,
                        "description": migration_instance.description,
                        "created_at": migration_file.stat().st_mtime,
                        "status": "available"
                    })
                except Exception as e:
                    migrations_info.append({
                        "file": migration_file.name,
                        "description": "Failed to load",
                        "error": str(e),
                        "status": "error"
                    })
            
            return ResponseFormatter.success(
                message=f"Found {len(migrations_info)} migrations",
                data={
                    "total_migrations": len(migrations_info),
                    "migrations": migrations_info
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get migration status: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get migration status: {str(e)}"
            )
    
    def _get_migration_files(self, reverse: bool = False) -> List[Path]:
        """Get all migration files sorted by name"""
        if not self.migrations_dir.exists():
            logger.warning(f"Migrations directory not found: {self.migrations_dir}")
            return []
        
        migration_files = []
        for file_path in self.migrations_dir.glob("migration_*.py"):
            if file_path.name != "migration_manager.py":  # Skip the manager file
                migration_files.append(file_path)
        
        # Sort by filename (which includes timestamp)
        migration_files.sort(reverse=reverse)
        return migration_files
    
    def _import_migration(self, migration_file: Path):
        """Import a migration class from file"""
        spec = importlib.util.spec_from_file_location(
            migration_file.stem, 
            migration_file
        )
        
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load migration from {migration_file}")
        
        module = importlib.util.module_from_spec(spec)
        
        # Add to sys.modules to handle relative imports
        sys.modules[migration_file.stem] = module
        
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            # Clean up sys.modules on failure
            if migration_file.stem in sys.modules:
                del sys.modules[migration_file.stem]
            raise e
        
        # Find the migration class (should end with 'Migration')
        migration_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                attr_name.endswith('Migration') and 
                attr_name != 'BaseMigration'):
                migration_class = attr
                break
        
        if migration_class is None:
            raise ImportError(f"No migration class found in {migration_file}")
        
        return migration_class 