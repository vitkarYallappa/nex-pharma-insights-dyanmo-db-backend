"""
Project Controller
Works with ProjectService and handles API requests/responses
Follows the same pattern as UserController for consistency
"""

from typing import List, Optional, Dict, Any
from app.services.project_service import ProjectService, ProjectNotFoundException, ProjectAlreadyExistsException
from app.use_cases.project_request_creation_service import ProjectRequestCreationOrchestrator, ProjectRequestCreationException
from app.use_cases.project_recent_feeds_service import ProjectRecentFeedsService
from app.use_cases.project_statistics_service import ProjectStatisticsService
from app.core.response import ResponseFormatter, APIResponse, to_response_format
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("project_controller")

class ProjectController:
    """Project controller with essential operations"""
    
    def __init__(self):
        self.project_service = ProjectService()
        self.project_request_orchestrator = ProjectRequestCreationOrchestrator()
        self.project_recent_feeds_service = ProjectRecentFeedsService()
        self.project_statistics_service = ProjectStatisticsService()
        self.logger = logger
    
    async def create_project(self, name: str, created_by: str, description: Optional[str] = None,
                            status: Optional[str] = None, project_metadata: Optional[Dict[str, Any]] = None,
                            module_config: Optional[Dict[str, Any]] = None,
                            request_id: Optional[str] = None) -> APIResponse:
        """Create a new project"""
        try:
            project = await self.project_service.create_project(
                name=name,
                created_by=created_by,
                description=description,
                status=status,
                project_metadata=project_metadata,
                module_config=module_config
            )
            
            self.logger.info(f"Project created successfully: {name}")
            return ResponseFormatter.created(
                data=project.to_response(),
                message=f"Project '{name}' created successfully",
                request_id=request_id
            )
            
        except ValidationException as e:
            self.logger.error(f"Project creation validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=request_id
            )
            
        except ProjectAlreadyExistsException as e:
            self.logger.error(f"Project creation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "name", "message": "Project name already exists"}],
                request_id=request_id
            )
            
        except Exception as e:
            self.logger.error(f"Project creation failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to create project",
                errors=[{"error": str(e)}],
                request_id=request_id
            )
    
    async def get_project_by_id(self, project_id: str, request_id: Optional[str] = None) -> APIResponse:
        """Get project by ID"""
        try:
            project = await self.project_service.get_project_by_id(project_id)
            
            self.logger.info(f"Project retrieved successfully: {project_id}")
            return ResponseFormatter.success(
                data=to_response_format(project),
                message=f"Project retrieved successfully",
                request_id=request_id
            )
            
        except ValidationException as e:
            self.logger.error(f"Project retrieval validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "project_id", "message": str(e)}],
                request_id=request_id
            )
            
        except ProjectNotFoundException as e:
            self.logger.error(f"Project not found: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "project_id", "message": "Project not found"}],
                request_id=request_id
            )
            
        except Exception as e:
            self.logger.error(f"Project retrieval failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to retrieve project",
                errors=[{"error": str(e)}],
                request_id=request_id
            )
    
    async def get_projects_by_query(self, status: Optional[str] = None, 
                                   created_by: Optional[str] = None,
                                   limit: Optional[int] = None,
                                   request_id: Optional[str] = None) -> APIResponse:
        """Get projects with optional filters"""
        try:
            projects = await self.project_service.get_projects_by_query(
                status=status,
                created_by=created_by,
                limit=limit
            )
            
            projects_data = [to_response_format(project) for project in projects]
            
            # Build filter description for message
            filters = []
            if status:
                filters.append(f"status={status}")
            if created_by:
                filters.append(f"created_by={created_by}")
            if limit:
                filters.append(f"limit={limit}")
            
            filter_desc = f" with filters: {', '.join(filters)}" if filters else ""
            
            self.logger.info(f"Retrieved {len(projects)} projects{filter_desc}")
            return ResponseFormatter.success(
                data={
                    "projects": projects_data,
                    "count": len(projects_data),
                    "filters": {
                        "status": status,
                        "created_by": created_by,
                        "limit": limit
                    }
                },
                message=f"Retrieved {len(projects)} projects{filter_desc}",
                request_id=request_id
            )
            
        except ValidationException as e:
            self.logger.error(f"Project query validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=request_id
            )
            
        except Exception as e:
            self.logger.error(f"Project query failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to retrieve projects",
                errors=[{"error": str(e)}],
                request_id=request_id
            )
    
    async def create_project_request_with_details(self, payload: Dict[str, Any], request_id: Optional[str] = None) -> APIResponse:
        """Create a complete project request with all related entities through orchestration"""
        try:
            self.logger.info(f"Starting project request creation orchestration: {payload.get('title', 'Unknown')}")
            
            # Execute orchestration through the use case layer
            result = await self.project_request_orchestrator.create_project_request_from_payload(payload)
            
            self.logger.info(f"Project request orchestration completed successfully - Orchestration ID: {result['orchestration_id']}")
            
            return ResponseFormatter.created(
                data=result,
                message="Project request created successfully with all related entities",
                request_id=request_id
            )
            
        except ProjectRequestCreationException as e:
            self.logger.error(f"Project request creation orchestration failed: {str(e)}")
            return ResponseFormatter.error(
                message=f"Project request creation failed: {str(e)}",
                errors=[{"field": "orchestration", "message": str(e)}],
                request_id=request_id
            )
            
        except ValidationException as e:
            self.logger.error(f"Project request creation validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=request_id
            )
            
        except Exception as e:
            self.logger.error(f"Unexpected error during project request creation: {str(e)}")
            return ResponseFormatter.error(
                message="Internal server error during project request creation",
                errors=[{"error": str(e)}],
                request_id=request_id
            )
    
    async def get_recent_content_feeds(self, limit: Optional[int] = 5, request_id: Optional[str] = None) -> APIResponse:
        """Get recent content feeds with insights and implications count (limited to maximum 5 items)"""
        try:
            self.logger.info("Starting recent content feeds retrieval")
            
            # Execute through the use case layer with limit
            result = await self.project_recent_feeds_service.get_recent_feeds(limit=limit)
            
            self.logger.info(f"Recent content feeds retrieval completed - {result['total_projects']} projects processed")
            
            return ResponseFormatter.success(
                data=result,
                message=result.get('message', 'Recent content feeds retrieved successfully'),
                request_id=request_id
            )
            
        except ValidationException as e:
            self.logger.error(f"Recent content feeds validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=request_id
            )
            
        except Exception as e:
            self.logger.error(f"Unexpected error during recent content feeds retrieval: {str(e)}")
            return ResponseFormatter.error(
                message="Internal server error during recent content feeds retrieval",
                errors=[{"error": str(e)}],
                request_id=request_id
            )
    
    async def get_dashboard_statistics(self, request_id: Optional[str] = None) -> APIResponse:
        """Get comprehensive dashboard statistics for reporting"""
        try:
            self.logger.info("Starting dashboard statistics retrieval")
            
            # Execute through the use case layer
            result = await self.project_statistics_service.get_dashboard_statistics()
            
            self.logger.info("Dashboard statistics retrieval completed successfully")
            
            return ResponseFormatter.success(
                data=result,
                message=result.get('message', 'Dashboard statistics retrieved successfully'),
                request_id=request_id
            )
            
        except ValidationException as e:
            self.logger.error(f"Dashboard statistics validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=request_id
            )
            
        except Exception as e:
            self.logger.error(f"Unexpected error during dashboard statistics retrieval: {str(e)}")
            return ResponseFormatter.error(
                message="Internal server error during dashboard statistics retrieval",
                errors=[{"error": str(e)}],
                request_id=request_id
            )
    
    async def get_project_breakdown_statistics(self, limit: Optional[int] = None, request_id: Optional[str] = None) -> APIResponse:
        """Get detailed project breakdown statistics"""
        try:
            self.logger.info("Starting project breakdown statistics retrieval")
            
            # Execute through the use case layer
            result = await self.project_statistics_service.get_project_breakdown_statistics(limit=limit)
            
            self.logger.info("Project breakdown statistics retrieval completed successfully")
            
            return ResponseFormatter.success(
                data=result,
                message=result.get('message', 'Project breakdown statistics retrieved successfully'),
                request_id=request_id
            )
            
        except ValidationException as e:
            self.logger.error(f"Project breakdown statistics validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=request_id
            )
            
        except Exception as e:
            self.logger.error(f"Unexpected error during project breakdown statistics retrieval: {str(e)}")
            return ResponseFormatter.error(
                message="Internal server error during project breakdown statistics retrieval",
                errors=[{"error": str(e)}],
                request_id=request_id
            )
    
    async def get_global_resources_statistics(self, request_id: Optional[str] = None) -> APIResponse:
        """Get global resources statistics (keywords and URLs)"""
        try:
            self.logger.info("Starting global resources statistics retrieval")
            
            # Execute through the use case layer
            result = await self.project_statistics_service.get_global_resources_statistics()
            
            self.logger.info("Global resources statistics retrieval completed successfully")
            
            return ResponseFormatter.success(
                data=result,
                message=result.get('message', 'Global resources statistics retrieved successfully'),
                request_id=request_id
            )
            
        except ValidationException as e:
            self.logger.error(f"Global resources statistics validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=request_id
            )
            
        except Exception as e:
            self.logger.error(f"Unexpected error during global resources statistics retrieval: {str(e)}")
            return ResponseFormatter.error(
                message="Internal server error during global resources statistics retrieval",
                errors=[{"error": str(e)}],
                request_id=request_id
            )
    
 