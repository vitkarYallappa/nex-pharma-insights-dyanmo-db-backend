"""
Process Handling Model - Matches SQLAlchemy schema structure
Handles process handling data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config.table_configs.process_handling_table import ProcessHandlingTableConfig
from app.config.settings import settings

class ProcessHandlingModel(BaseModel):
    """Process handling model matching SQLAlchemy schema"""
    
    # SQLAlchemy: process_id (UUID) -> DynamoDB: pk (String)
    pk: str = Field(..., description="Process ID (UUID as string)")
    
    # SQLAlchemy: request_id (UUID) -> DynamoDB: request_id (String)
    request_id: str = Field(..., description="Request ID reference (UUID as string)")
    
    # SQLAlchemy: project_id (UUID) -> DynamoDB: project_id (String)
    project_id: str = Field(..., description="Project ID reference (UUID as string)")
    
    # SQLAlchemy: status (String) -> DynamoDB: status (String)
    status: str = Field(..., description="Process status")
    
    # SQLAlchemy: priority (Integer) -> DynamoDB: priority (Number)
    priority: Optional[int] = Field(None, description="Process priority")
    
    # SQLAlchemy: total_records_expected (Integer) -> DynamoDB: total_records_expected (Number)
    total_records_expected: Optional[int] = Field(None, description="Expected records count")
    
    # SQLAlchemy: records_processed (Integer) -> DynamoDB: records_processed (Number)
    records_processed: Optional[int] = Field(None, description="Processed records count")
    
    # SQLAlchemy: records_successful (Integer) -> DynamoDB: records_successful (Number)
    records_successful: Optional[int] = Field(None, description="Successful records count")
    
    # SQLAlchemy: records_failed (Integer) -> DynamoDB: records_failed (Number)
    records_failed: Optional[int] = Field(None, description="Failed records count")
    
    # SQLAlchemy: processing_notes (Text) -> DynamoDB: processing_notes (String)
    processing_notes: Optional[str] = Field(None, description="Processing notes")
    
    # SQLAlchemy: assigned_worker (String) -> DynamoDB: assigned_worker (String)
    assigned_worker: Optional[str] = Field(None, description="Assigned worker")
    
    # SQLAlchemy: created_at (DateTime) -> DynamoDB: created_at (String)
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    
    # SQLAlchemy: started_at (DateTime) -> DynamoDB: started_at (String)
    started_at: Optional[str] = Field(None, description="Start timestamp (ISO string)")
    
    # SQLAlchemy: completed_at (DateTime) -> DynamoDB: completed_at (String)
    completed_at: Optional[str] = Field(None, description="Completion timestamp (ISO string)")
    
    # SQLAlchemy: updated_at (DateTime) -> DynamoDB: updated_at (String)
    updated_at: Optional[str] = Field(None, description="Last update timestamp (ISO string)")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return ProcessHandlingTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
    
    @classmethod
    def create_new(cls, request_id: str, project_id: str, status: str,
                   priority: Optional[int] = None, total_records_expected: Optional[int] = None,
                   processing_notes: Optional[str] = None, assigned_worker: Optional[str] = None) -> 'ProcessHandlingModel':
        """Create a new process handling instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            request_id=request_id,
            project_id=project_id,
            status=status,
            priority=priority,
            total_records_expected=total_records_expected,
            records_processed=0,
            records_successful=0,
            records_failed=0,
            processing_notes=processing_notes,
            assigned_worker=assigned_worker,
            created_at=now,
            started_at=None,
            completed_at=None,
            updated_at=now
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        data = self.model_dump()
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessHandlingModel':
        """Create model instance from DynamoDB data"""
        return cls(**data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "process_id": self.pk,  # Return as 'process_id' for API consistency
            "request_id": self.request_id,
            "project_id": self.project_id,
            "status": self.status,
            "priority": self.priority,
            "total_records_expected": self.total_records_expected,
            "records_processed": self.records_processed,
            "records_successful": self.records_successful,
            "records_failed": self.records_failed,
            "processing_notes": self.processing_notes,
            "assigned_worker": self.assigned_worker,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "updated_at": self.updated_at
        }
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields and set updated_at timestamp"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['pk', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow().isoformat()
    
    def start_processing(self) -> None:
        """Mark process as started"""
        self.status = "processing"
        self.started_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def complete_processing(self) -> None:
        """Mark process as completed"""
        self.status = "completed"
        self.completed_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def fail_processing(self, notes: Optional[str] = None) -> None:
        """Mark process as failed"""
        self.status = "failed"
        if notes:
            self.processing_notes = notes
        self.completed_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat() 