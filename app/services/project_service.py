"""
Project Service - Works with ProjectModel and ProjectRepository
Follows the same pattern as UserService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.project_repository import ProjectRepository
from app.models.project_model import ProjectModel
from app.core.logging import get_logger
from app.core.exceptions import (
    UserNotFoundException,
    ValidationException
)

logger = get_logger("project_service")

class ProjectNotFoundException(Exception):
    """Exception raised when project is not found"""
    pass

class ProjectAlreadyExistsException(Exception):
    """Exception raised when project already exists"""
    pass

class ProjectService:
    """Project service with essential operations"""
    
    def __init__(self):
        self.project_repository = ProjectRepository()
        self.logger = logger
    
    async def create_project(self, name: str, created_by: str, description: Optional[str] = None,
                            status: Optional[str] = None, project_metadata: Optional[Dict[str, Any]] = None,
                            module_config: Optional[Dict[str, Any]] = None) -> ProjectModel:
        """Create a new project"""
        try:
            # Validate required fields
            if not name or not name.strip():
                raise ValidationException("Project name is required")
            
            if not created_by or not created_by.strip():
                raise ValidationException("Creator ID is required")
            
            # Create project model
            project_model = ProjectModel.create_new(
                name=name.strip(),
                created_by=created_by.strip(),
                description=description.strip() if description else None,
                status=status or "active",
                project_metadata=project_metadata or {},
                module_config=module_config or {}
            )
            
            # Save to database
            created_project = await self.project_repository.create(project_model)
            self.logger.info(f"Project created: {name} by {created_by}")
            return created_project
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create project failed: {str(e)}")
            raise
    
    async def get_project_by_id(self, project_id: str) -> ProjectModel:
        """Get project by ID"""
        try:
            if not project_id or not project_id.strip():
                raise ValidationException("Project ID is required")
            
            project = await self.project_repository.find_one_by_query({"pk": project_id.strip()})
            if not project:
                raise ProjectNotFoundException(f"Project with ID {project_id} not found")
            
            return project
            
        except (ProjectNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get project by ID failed: {str(e)}")
            raise
    
    async def get_projects_by_query(self, status: Optional[str] = None, 
                                   created_by: Optional[str] = None,
                                   limit: Optional[int] = None) -> List[ProjectModel]:
        """Get projects with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            projects = await self.project_repository.get_all_projects(
                status=status.strip() if status else None,
                created_by=created_by.strip() if created_by else None,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(projects)} projects with filters: status={status}, created_by={created_by}")
            return projects
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get projects by query failed: {str(e)}")
            raise
    

    
    async def update_project(self, project_id: str, update_data: Dict[str, Any]) -> ProjectModel:
        """Update project by ID"""
        try:
            if not project_id or not project_id.strip():
                raise ValidationException("Project ID is required")
            
            # Check if project exists
            existing_project = await self.get_project_by_id(project_id)
            
            # Prepare update data (remove None values and add updated_at)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            if clean_update_data:
                from datetime import datetime
                clean_update_data["updated_at"] = datetime.utcnow().isoformat()
            
            updated_project = await self.project_repository.update_project(
                project_id.strip(), clean_update_data
            )
            
            if not updated_project:
                raise ProjectNotFoundException(f"Failed to update project with ID {project_id}")
            
            self.logger.info(f"Project updated: {project_id}")
            return updated_project
            
        except (ProjectNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update project failed: {str(e)}")
            raise 