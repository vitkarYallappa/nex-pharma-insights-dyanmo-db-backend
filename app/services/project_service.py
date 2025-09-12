"""
Project Service - Works with ProjectModel and ProjectRepository
Follows the same pattern as UserService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.project_repository import ProjectRepository
from app.models.project_model import ProjectModel
from app.services.requests_service import RequestsService
from app.services.keywords_service import KeywordsService
from app.services.source_urls_service import SourceUrlsService
from app.services.content_repository_service import ContentRepositoryService
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
        self.requests_service = RequestsService()
        self.keywords_service = KeywordsService()
        self.source_urls_service = SourceUrlsService()
        self.content_repository_service = ContentRepositoryService()
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

            project = await self._enrich_single_project_with_request_data(project)

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

            # Enrich projects with request data
            for i, project in enumerate(projects):
                enriched_project = await self._enrich_single_project_with_request_data(project)
                projects[i] = enriched_project



            self.logger.info(f"Retrieved {len(projects)} projects with filters: status={status}, created_by={created_by}")
            return projects
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get projects by query failed: {str(e)}")
            raise
    

    async def _enrich_single_project_with_request_data(self, project) -> Any:
        """
        Enrich a single project with its associated request data
        
        Args:
            project: Single project model or dict to enrich
            
        Returns:
            Enriched project with request data attached
        """
        try:
            project_id = project.get("pk") if hasattr(project, 'get') else project.pk
            
            # Get the single request for this project
            request = await self.requests_service.find_one_by_query(project_id=project_id)
            
            if request:
                request_id = request.get("pk") if hasattr(request, 'get') else request.pk
                request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
                
                # Get keywords count for this request
                keywords = await self.keywords_service.get_keyword_by_query(request_id=request_id)
                keywords = [item.keyword for item in keywords]
                keywords_count = len(keywords)
                
                # Get source URLs count for this request
                source_urls = await self.source_urls_service.get_source_urls_by_query(request_id=request_id)
                source_urls_count = len(source_urls)
                
                # Get content repository count for this project
                content_repositories = await self.content_repository_service.get_all_content_repository(project_id=project_id)
                content_repository_count = len(content_repositories)
                
                # Create request info
                request_info = {
                    "request_id": request_id,
                    # "description": request_dict.get("description"),
                    # "title": request_dict.get("title"),
                    "status": request_dict.get("status"),
                    # "priority": request_dict.get("priority"),
                    "keywords_count": keywords_count,
                    "keywords_list": keywords,
                    "source_urls_count": source_urls_count,
                    "content_repository_count": content_repository_count
                }
                
                # Update project with request data
                if hasattr(project, 'update'):
                    project.update({
                        "request": request_info,
                        "has_request": True
                    })
                    return project
                else:
                    # If project is a model object, convert to dict and update
                    project_dict = project.to_dict() if hasattr(project, 'to_dict') else project
                    project_dict.update({
                        "request": request_info,
                        "has_request": True
                    })
                    return project_dict
            else:
                # No request found for this project
                if hasattr(project, 'update'):
                    project.update({
                        "request": None,
                        "has_request": False
                    })
                    return project
                else:
                    # If project is a model object, convert to dict and update
                    project_dict = project.to_dict() if hasattr(project, 'to_dict') else project
                    project_dict.update({
                        "request": None,
                        "has_request": False
                    })
                    return project_dict
                    
        except Exception as e:
            self.logger.error(f"Failed to enrich single project with request data: {str(e)}")
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