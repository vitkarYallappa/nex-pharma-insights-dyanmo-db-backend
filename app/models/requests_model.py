"""
Requests Model - Matches SQLAlchemy schema structure
Handles requests data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config.table_configs.requests_table import RequestsTableConfig
from app.config.settings import settings

class RequestsModel(BaseModel):
    """Requests model matching SQLAlchemy schema"""
    
    # SQLAlchemy: id (UUID) -> DynamoDB: pk (String)
    pk: str = Field(..., description="Request ID (UUID as string)")
    
    # SQLAlchemy: project_id (UUID) -> DynamoDB: project_id (String)
    project_id: str = Field(..., description="Project ID reference (UUID as string)")
    
    # SQLAlchemy: title (String) -> DynamoDB: title (String)
    title: str = Field(..., description="Request title")
    
    # SQLAlchemy: description (Text) -> DynamoDB: description (String)
    description: Optional[str] = Field(None, description="Request description")
    
    # SQLAlchemy: time_range (JSON) -> DynamoDB: time_range (Map)
    time_range: Optional[Dict[str, Any]] = Field(None, description="Time range JSON")
    
    # SQLAlchemy: priority (String) -> DynamoDB: priority (String)
    priority: Optional[str] = Field(None, description="Request priority")
    
    # SQLAlchemy: status (String) -> DynamoDB: status (String)
    status: Optional[str] = Field(None, description="Request status")
    
    # SQLAlchemy: estimated_completion (DateTime) -> DynamoDB: estimated_completion (String)
    estimated_completion: Optional[str] = Field(None, description="Estimated completion timestamp (ISO string)")
    
    # SQLAlchemy: created_by (UUID) -> DynamoDB: created_by (String)
    created_by: str = Field(..., description="Creator user ID (UUID as string)")
    
    # SQLAlchemy: created_at (DateTime) -> DynamoDB: created_at (String)
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    
    # SQLAlchemy: updated_at (DateTime) -> DynamoDB: updated_at (String)
    updated_at: Optional[str] = Field(None, description="Last update timestamp (ISO string)")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return RequestsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
    
    @classmethod
    def create_new(cls, project_id: str, title: str, created_by: str, description: Optional[str] = None,
                   time_range: Optional[Dict[str, Any]] = None, priority: Optional[str] = None,
                   status: Optional[str] = None, estimated_completion: Optional[str] = None) -> 'RequestsModel':
        """Create a new request instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            project_id=project_id,
            title=title,
            description=description,
            time_range=time_range or {},
            priority=priority,
            status=status or "pending",
            estimated_completion=estimated_completion,
            created_by=created_by,
            created_at=now,
            updated_at=now
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        data = self.model_dump()
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RequestsModel':
        """Create model instance from DynamoDB data"""
        return cls(**data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "id": self.pk,  # Return as 'id' for API consistency
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "time_range": self.time_range,
            "priority": self.priority,
            "status": self.status,
            "estimated_completion": self.estimated_completion,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields and set updated_at timestamp"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['pk', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow().isoformat() 