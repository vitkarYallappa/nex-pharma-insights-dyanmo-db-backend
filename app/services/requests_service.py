"""
Requests Service - Works with RequestsModel and RequestsRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.requests_repository import RequestsRepository
from app.models.requests_model import RequestsModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("requests_service")

class RequestsNotFoundException(Exception):
    """Exception raised when request is not found"""
    pass

class RequestsAlreadyExistsException(Exception):
    """Exception raised when request already exists"""
    pass

class RequestsService:
    """Requests service with essential operations"""
    
    def __init__(self):
        self.requests_repository = RequestsRepository()
        self.logger = logger
    
    async def create_request(self, project_id: str, title: str, created_by: str, description: Optional[str] = None,
                            time_range: Optional[Dict[str, Any]] = None, priority: Optional[str] = None,
                            status: Optional[str] = None, estimated_completion: Optional[str] = None) -> RequestsModel:
        """Create a new request"""
        try:
            # Validate required fields
            if not project_id or not project_id.strip():
                raise ValidationException("Project ID is required")
            
            if not title or not title.strip():
                raise ValidationException("Request title is required")
            
            if not created_by or not created_by.strip():
                raise ValidationException("Creator ID is required")
            
            # Create request model
            request_model = RequestsModel.create_new(
                project_id=project_id.strip(),
                title=title.strip(),
                created_by=created_by.strip(),
                description=description.strip() if description else None,
                time_range=time_range or {},
                priority=priority,
                status=status or "pending",
                estimated_completion=estimated_completion
            )
            
            # Save to database
            created_request = await self.requests_repository.create(request_model)
            self.logger.info(f"Request created: {title} for project {project_id}")
            return created_request
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create request failed: {str(e)}")
            raise
    
    async def find_one_by_query(self, request_id: Optional[str] = None, project_id: Optional[str] = None) -> RequestsModel:
        """Get request by request_id or project_id"""
        try:
            # Validate that at least one parameter is provided
            if not request_id and not project_id:
                raise ValidationException("Either request_id or project_id is required")
            
            # Validate that only one parameter is provided
            if request_id and project_id:
                raise ValidationException("Provide either request_id or project_id, not both")

            # Build query based on provided parameter
            if request_id:
                if not request_id.strip():
                    raise ValidationException("Request ID cannot be empty")
                query = {"pk": request_id.strip()}
            else:  # project_id is provided
                if not project_id.strip():
                    raise ValidationException("Project ID cannot be empty")
                query = {"project_id": project_id.strip()}

            request = await self.requests_repository.find_one_by_query(query)
            if not request:
                identifier = request_id if request_id else project_id
                identifier_type = "request_id" if request_id else "project_id"
                raise RequestsNotFoundException(f"Request with {identifier_type} {identifier} not found")

            return request

        except (RequestsNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get request by query failed: {str(e)}")
            raise
    
    async def get_request_by_query(self, project_id: Optional[str] = None,
                                   status: Optional[str] = None,
                                   priority: Optional[str] = None,
                                   created_by: Optional[str] = None,
                                   limit: Optional[int] = None) -> List[RequestsModel]:
        """Get requests with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            requests = await self.requests_repository.get_all_requests(
                project_id=project_id.strip() if project_id else None,
                status=status.strip() if status else None,
                priority=priority.strip() if priority else None,
                created_by=created_by.strip() if created_by else None,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(requests)} requests with filters: project_id={project_id}, status={status}, priority={priority}, created_by={created_by}")
            return requests
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get requests by query failed: {str(e)}")
            raise
    
    async def update_request(self, request_id: str, update_data: Dict[str, Any]) -> RequestsModel:
        """Update request by ID"""
        try:
            if not request_id or not request_id.strip():
                raise ValidationException("Request ID is required")
            
            # Check if request exists
            existing_request = await self.find_one_by_query(request_id=request_id)
            
            # Prepare update data (remove None values and add updated_at)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            if clean_update_data:
                from datetime import datetime
                clean_update_data["updated_at"] = datetime.utcnow().isoformat()
            
            updated_request = await self.requests_repository.update_request(
                request_id.strip(), clean_update_data
            )
            
            if not updated_request:
                raise RequestsNotFoundException(f"Failed to update request with ID {request_id}")
            
            self.logger.info(f"Request updated: {request_id}")
            return updated_request
            
        except (RequestsNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update request failed: {str(e)}")
            raise 