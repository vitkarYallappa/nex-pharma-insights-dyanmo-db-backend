"""
Project Request Statistics Model - Matches SQLAlchemy schema structure
Handles project request statistics data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config.table_configs.project_request_statistics_table import ProjectRequestStatisticsTableConfig
from app.config.settings import settings

class ProjectRequestStatisticsModel(BaseModel):
    """Project request statistics model matching SQLAlchemy schema"""
    
    # SQLAlchemy: id (UUID) -> DynamoDB: pk (String)
    pk: str = Field(..., description="Statistics ID (UUID as string)")
    
    # SQLAlchemy: project_id (UUID) -> DynamoDB: project_id (String)
    project_id: str = Field(..., description="Project ID reference (UUID as string)")
    
    # SQLAlchemy: total_requests (Integer) -> DynamoDB: total_requests (Number)
    total_requests: Optional[int] = Field(None, description="Total request count")
    
    # SQLAlchemy: completed_requests (Integer) -> DynamoDB: completed_requests (Number)
    completed_requests: Optional[int] = Field(None, description="Completed request count")
    
    # SQLAlchemy: pending_requests (Integer) -> DynamoDB: pending_requests (Number)
    pending_requests: Optional[int] = Field(None, description="Pending request count")
    
    # SQLAlchemy: failed_requests (Integer) -> DynamoDB: failed_requests (Number)
    failed_requests: Optional[int] = Field(None, description="Failed request count")
    
    # SQLAlchemy: average_processing_time (str) -> DynamoDB: average_processing_time (Number)
    average_processing_time: Optional[int] = Field(None, description="Average processing time in seconds")
    
    # SQLAlchemy: last_activity_at (DateTime) -> DynamoDB: last_activity_at (String)
    last_activity_at: Optional[str] = Field(None, description="Last activity timestamp (ISO string)")
    
    # SQLAlchemy: statistics_metadata (JSON) -> DynamoDB: statistics_metadata (Map)
    statistics_metadata: Optional[Dict[str, Any]] = Field(None, description="Statistics metadata JSON")
    
    # SQLAlchemy: created_at (DateTime) -> DynamoDB: created_at (String)
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    
    # SQLAlchemy: updated_at (DateTime) -> DynamoDB: updated_at (String)
    updated_at: Optional[str] = Field(None, description="Last update timestamp (ISO string)")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return ProjectRequestStatisticsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
    
    @classmethod
    def create_new(cls, project_id: str, total_requests: Optional[int] = None,
                   completed_requests: Optional[int] = None, pending_requests: Optional[int] = None,
                   failed_requests: Optional[int] = None, average_processing_time: Optional[int] = None,
                   last_activity_at: Optional[str] = None, statistics_metadata: Optional[Dict[str, Any]] = None) -> 'ProjectRequestStatisticsModel':
        """Create a new project request statistics instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            project_id=project_id,
            total_requests=total_requests,
            completed_requests=completed_requests,
            pending_requests=pending_requests,
            failed_requests=failed_requests,
            average_processing_time=average_processing_time,
            last_activity_at=last_activity_at,
            statistics_metadata=statistics_metadata or {},
            created_at=now,
            updated_at=now
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        data = self.model_dump()
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectRequestStatisticsModel':
        """Create model instance from DynamoDB data"""
        return cls(**data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "id": self.pk,  # Return as 'id' for API consistency
            "project_id": self.project_id,
            "total_requests": self.total_requests,
            "completed_requests": self.completed_requests,
            "pending_requests": self.pending_requests,
            "failed_requests": self.failed_requests,
            "average_processing_time": self.average_processing_time,
            "last_activity_at": self.last_activity_at,
            "statistics_metadata": self.statistics_metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields and set updated_at timestamp"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['pk', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow().isoformat() 