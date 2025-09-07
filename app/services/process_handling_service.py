"""
Process Handling Service - Works with ProcessHandlingModel and ProcessHandlingRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.process_handling_repository import ProcessHandlingRepository
from app.models.process_handling_model import ProcessHandlingModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("process_handling_service")

class ProcessHandlingNotFoundException(Exception):
    """Exception raised when process handling entry is not found"""
    pass

class ProcessHandlingAlreadyExistsException(Exception):
    """Exception raised when process handling entry already exists"""
    pass

class ProcessHandlingService:
    """Process handling service with essential operations"""
    
    def __init__(self):
        self.process_repository = ProcessHandlingRepository()
        self.logger = logger
    
    async def create_project(self, request_id: str, project_id: str, status: str,
                            priority: Optional[int] = None, total_records_expected: Optional[int] = None,
                            processing_notes: Optional[str] = None, assigned_worker: Optional[str] = None) -> ProcessHandlingModel:
        """Create a new process handling entry"""
        try:
            # Validate required fields
            if not request_id or not request_id.strip():
                raise ValidationException("Request ID is required")
            
            if not project_id or not project_id.strip():
                raise ValidationException("Project ID is required")
            
            if not status or not status.strip():
                raise ValidationException("Status is required")
            
            # Create process model
            process_model = ProcessHandlingModel.create_new(
                request_id=request_id.strip(),
                project_id=project_id.strip(),
                status=status.strip(),
                priority=priority,
                total_records_expected=total_records_expected,
                processing_notes=processing_notes.strip() if processing_notes else None,
                assigned_worker=assigned_worker.strip() if assigned_worker else None
            )
            
            # Save to database
            created_process = await self.process_repository.create(process_model)
            self.logger.info(f"Process handling entry created: {status} for request {request_id}")
            return created_process
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create process handling entry failed: {str(e)}")
            raise
    
    async def get_project_by_id(self, process_id: str) -> ProcessHandlingModel:
        """Get process handling entry by ID"""
        try:
            if not process_id or not process_id.strip():
                raise ValidationException("Process ID is required")
            
            process = await self.process_repository.find_one_by_query({"pk": process_id.strip()})
            if not process:
                raise ProcessHandlingNotFoundException(f"Process handling entry with ID {process_id} not found")
            
            return process
            
        except (ProcessHandlingNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get process handling entry by ID failed: {str(e)}")
            raise
    
    async def get_projects_by_query(self, request_id: Optional[str] = None,
                                   project_id: Optional[str] = None,
                                   status: Optional[str] = None,
                                   assigned_worker: Optional[str] = None,
                                   priority: Optional[int] = None,
                                   limit: Optional[int] = None) -> List[ProcessHandlingModel]:
        """Get process handling entries with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            processes = await self.process_repository.get_all_projects(
                request_id=request_id.strip() if request_id else None,
                project_id=project_id.strip() if project_id else None,
                status=status.strip() if status else None,
                assigned_worker=assigned_worker.strip() if assigned_worker else None,
                priority=priority,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(processes)} process handling entries with filters: request_id={request_id}, project_id={project_id}, status={status}, assigned_worker={assigned_worker}, priority={priority}")
            return processes
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get process handling entries by query failed: {str(e)}")
            raise
    
    async def update_project(self, process_id: str, update_data: Dict[str, Any]) -> ProcessHandlingModel:
        """Update process handling entry by ID"""
        try:
            if not process_id or not process_id.strip():
                raise ValidationException("Process ID is required")
            
            # Check if process exists
            existing_process = await self.get_project_by_id(process_id)
            
            # Prepare update data (remove None values and add updated_at)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            if clean_update_data:
                from datetime import datetime
                clean_update_data["updated_at"] = datetime.utcnow().isoformat()
            
            updated_process = await self.process_repository.update_project(
                process_id.strip(), clean_update_data
            )
            
            if not updated_process:
                raise ProcessHandlingNotFoundException(f"Failed to update process handling entry with ID {process_id}")
            
            self.logger.info(f"Process handling entry updated: {process_id}")
            return updated_process
            
        except (ProcessHandlingNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update process handling entry failed: {str(e)}")
            raise
    
    async def start_process(self, process_id: str) -> ProcessHandlingModel:
        """Start a process"""
        try:
            process = await self.get_project_by_id(process_id)
            process.start_processing()
            
            updated_process = await self.process_repository.update_project(
                process_id, process.to_dict()
            )
            
            if not updated_process:
                raise ProcessHandlingNotFoundException(f"Failed to start process with ID {process_id}")
            
            self.logger.info(f"Process started: {process_id}")
            return updated_process
            
        except (ProcessHandlingNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Start process failed: {str(e)}")
            raise
    
    async def complete_process(self, process_id: str) -> ProcessHandlingModel:
        """Complete a process"""
        try:
            process = await self.get_project_by_id(process_id)
            process.complete_processing()
            
            updated_process = await self.process_repository.update_project(
                process_id, process.to_dict()
            )
            
            if not updated_process:
                raise ProcessHandlingNotFoundException(f"Failed to complete process with ID {process_id}")
            
            self.logger.info(f"Process completed: {process_id}")
            return updated_process
            
        except (ProcessHandlingNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Complete process failed: {str(e)}")
            raise
    
    async def fail_process(self, process_id: str, notes: Optional[str] = None) -> ProcessHandlingModel:
        """Fail a process"""
        try:
            process = await self.get_project_by_id(process_id)
            process.fail_processing(notes)
            
            updated_process = await self.process_repository.update_project(
                process_id, process.to_dict()
            )
            
            if not updated_process:
                raise ProcessHandlingNotFoundException(f"Failed to fail process with ID {process_id}")
            
            self.logger.info(f"Process failed: {process_id}")
            return updated_process
            
        except (ProcessHandlingNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Fail process failed: {str(e)}")
            raise 