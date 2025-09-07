"""
Project Request Statistics Service - Works with ProjectRequestStatisticsModel and ProjectRequestStatisticsRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.project_request_statistics_repository import ProjectRequestStatisticsRepository
from app.models.project_request_statistics_model import ProjectRequestStatisticsModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("project_request_statistics_service")

class ProjectRequestStatisticsNotFoundException(Exception):
    """Exception raised when project request statistics is not found"""
    pass

class ProjectRequestStatisticsAlreadyExistsException(Exception):
    """Exception raised when project request statistics already exists"""
    pass

class ProjectRequestStatisticsService:
    """Project request statistics service with essential operations"""
    
    def __init__(self):
        self.statistics_repository = ProjectRequestStatisticsRepository()
        self.logger = logger
    
    async def create_project(self, project_id: str, total_requests: Optional[int] = None,
                            completed_requests: Optional[int] = None, pending_requests: Optional[int] = None,
                            failed_requests: Optional[int] = None, average_processing_time: Optional[float] = None,
                            last_activity_at: Optional[str] = None, statistics_metadata: Optional[Dict[str, Any]] = None) -> ProjectRequestStatisticsModel:
        """Create a new project request statistics"""
        try:
            # Validate required fields
            if not project_id or not project_id.strip():
                raise ValidationException("Project ID is required")
            
            # Create statistics model
            statistics_model = ProjectRequestStatisticsModel.create_new(
                project_id=project_id.strip(),
                total_requests=total_requests,
                completed_requests=completed_requests,
                pending_requests=pending_requests,
                failed_requests=failed_requests,
                average_processing_time=average_processing_time,
                last_activity_at=last_activity_at,
                statistics_metadata=statistics_metadata or {}
            )
            
            # Save to database
            created_statistics = await self.statistics_repository.create(statistics_model)
            self.logger.info(f"Project request statistics created for project: {project_id}")
            return created_statistics
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create project request statistics failed: {str(e)}")
            raise
    
    async def get_project_by_id(self, statistics_id: str) -> ProjectRequestStatisticsModel:
        """Get project request statistics by ID"""
        try:
            if not statistics_id or not statistics_id.strip():
                raise ValidationException("Statistics ID is required")
            
            statistics = await self.statistics_repository.find_one_by_query({"pk": statistics_id.strip()})
            if not statistics:
                raise ProjectRequestStatisticsNotFoundException(f"Project request statistics with ID {statistics_id} not found")
            
            return statistics
            
        except (ProjectRequestStatisticsNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get project request statistics by ID failed: {str(e)}")
            raise
    
    async def get_projects_by_query(self, project_id: Optional[str] = None,
                                   limit: Optional[int] = None) -> List[ProjectRequestStatisticsModel]:
        """Get project request statistics with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            statistics = await self.statistics_repository.get_all_projects(
                project_id=project_id.strip() if project_id else None,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(statistics)} project request statistics with filters: project_id={project_id}")
            return statistics
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get project request statistics by query failed: {str(e)}")
            raise
    
    async def update_project(self, statistics_id: str, update_data: Dict[str, Any]) -> ProjectRequestStatisticsModel:
        """Update project request statistics by ID"""
        try:
            if not statistics_id or not statistics_id.strip():
                raise ValidationException("Statistics ID is required")
            
            # Check if statistics exists
            existing_statistics = await self.get_project_by_id(statistics_id)
            
            # Prepare update data (remove None values and add updated_at)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            if clean_update_data:
                from datetime import datetime
                clean_update_data["updated_at"] = datetime.utcnow().isoformat()
            
            updated_statistics = await self.statistics_repository.update_project(
                statistics_id.strip(), clean_update_data
            )
            
            if not updated_statistics:
                raise ProjectRequestStatisticsNotFoundException(f"Failed to update project request statistics with ID {statistics_id}")
            
            self.logger.info(f"Project request statistics updated: {statistics_id}")
            return updated_statistics
            
        except (ProjectRequestStatisticsNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update project request statistics failed: {str(e)}")
            raise 