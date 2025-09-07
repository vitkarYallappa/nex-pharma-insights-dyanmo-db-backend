"""
Project Modules Statistics Service - Works with ProjectModulesStatisticsModel and ProjectModulesStatisticsRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.project_modules_statistics_repository import ProjectModulesStatisticsRepository
from app.models.project_modules_statistics_model import ProjectModulesStatisticsModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("project_modules_statistics_service")

class ProjectModulesStatisticsNotFoundException(Exception):
    """Exception raised when project modules statistics is not found"""
    pass

class ProjectModulesStatisticsAlreadyExistsException(Exception):
    """Exception raised when project modules statistics already exists"""
    pass

class ProjectModulesStatisticsService:
    """Project modules statistics service with essential operations"""
    
    def __init__(self):
        self.statistics_repository = ProjectModulesStatisticsRepository()
        self.logger = logger
    
    async def create_project_modules_statistics(self, project_id: str, total_insights: Optional[int] = None,
                            total_implication: Optional[int] = None) -> ProjectModulesStatisticsModel:
        """Create a new project modules statistics"""
        try:
            # Validate required fields
            if not project_id or not project_id.strip():
                raise ValidationException("Project ID is required")
            
            # Create statistics model
            statistics_model = ProjectModulesStatisticsModel.create_new(
                project_id=project_id.strip(),
                total_insights=total_insights,
                total_implication=total_implication
            )
            
            # Save to database
            created_statistics = await self.statistics_repository.create(statistics_model)
            self.logger.info(f"Project modules statistics created for project: {project_id}")
            return created_statistics
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create project modules statistics failed: {str(e)}")
            raise
    
    async def get_project_modules_statistics_by_id(self, statistics_id: str) -> ProjectModulesStatisticsModel:
        """Get project modules statistics by ID"""
        try:
            if not statistics_id or not statistics_id.strip():
                raise ValidationException("Statistics ID is required")
            
            statistics = await self.statistics_repository.find_one_by_query({"pk": statistics_id.strip()})
            if not statistics:
                raise ProjectModulesStatisticsNotFoundException(f"Project modules statistics with ID {statistics_id} not found")
            
            return statistics
            
        except (ProjectModulesStatisticsNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get project modules statistics by ID failed: {str(e)}")
            raise
    
    async def get_project_modules_statistics_by_query(self, project_id: Optional[str] = None,
                                   limit: Optional[int] = None) -> List[ProjectModulesStatisticsModel]:
        """Get project modules statistics with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            statistics = await self.statistics_repository.get_all_project_modules_statistics(
                project_id=project_id.strip() if project_id else None,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(statistics)} project modules statistics with filters: project_id={project_id}")
            return statistics
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get project modules statistics by query failed: {str(e)}")
            raise
    
    async def update_project_modules_statistics(self, statistics_id: str, update_data: Dict[str, Any]) -> ProjectModulesStatisticsModel:
        """Update project modules statistics by ID"""
        try:
            if not statistics_id or not statistics_id.strip():
                raise ValidationException("Statistics ID is required")
            
            # Check if statistics exists
            existing_statistics = await self.get_project_modules_statistics_by_id(statistics_id)
            
            # Prepare update data (remove None values and add updated_at)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            if clean_update_data:
                from datetime import datetime
                clean_update_data["updated_at"] = datetime.utcnow().isoformat()
            
            updated_statistics = await self.statistics_repository.update_project_modules_statistics(
                statistics_id.strip(), clean_update_data
            )
            
            if not updated_statistics:
                raise ProjectModulesStatisticsNotFoundException(f"Failed to update project modules statistics with ID {statistics_id}")
            
            self.logger.info(f"Project modules statistics updated: {statistics_id}")
            return updated_statistics
            
        except (ProjectModulesStatisticsNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update project modules statistics failed: {str(e)}")
            raise 