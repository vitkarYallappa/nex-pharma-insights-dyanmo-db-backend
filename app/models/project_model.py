"""
Project Model - Matches SQLAlchemy schema structure
Handles project data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config.table_configs.projects_table import ProjectsTableConfig
from app.config.settings import settings

class ProjectModel(BaseModel):
    """Project model matching SQLAlchemy schema"""
    
    # SQLAlchemy: id (UUID) -> DynamoDB: pk (String)
    pk: str = Field(..., description="Project ID (UUID as string)")
    
    # SQLAlchemy: name (String) -> DynamoDB: name (String)
    name: str = Field(..., description="Project name")
    
    # SQLAlchemy: description (Text) -> DynamoDB: description (String)
    description: Optional[str] = Field(None, description="Project description")
    
    # SQLAlchemy: created_by (UUID) -> DynamoDB: created_by (String)
    created_by: str = Field(..., description="Creator user ID (UUID as string)")
    
    # SQLAlchemy: status (String) -> DynamoDB: status (String)
    status: Optional[str] = Field(None, description="Project status")
    
    # SQLAlchemy: project_metadata (JSON) -> DynamoDB: project_metadata (Map)
    project_metadata: Optional[Dict[str, Any]] = Field(None, description="Project metadata JSON")
    
    # SQLAlchemy: module_config (JSON) -> DynamoDB: module_config (Map)
    module_config: Optional[Dict[str, Any]] = Field(None, description="Module configuration JSON")
    
    # SQLAlchemy: created_at (DateTime) -> DynamoDB: created_at (String)
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    
    # SQLAlchemy: updated_at (DateTime) -> DynamoDB: updated_at (String)
    updated_at: Optional[str] = Field(None, description="Last update timestamp (ISO string)")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return ProjectsTableConfig.get_table_name()
    
    @classmethod
    def create_new(cls, name: str, created_by: str, description: Optional[str] = None,
                   status: Optional[str] = None, project_metadata: Optional[Dict[str, Any]] = None,
                   module_config: Optional[Dict[str, Any]] = None) -> 'ProjectModel':
        """Create a new project model instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            name=name,
            description=description,
            created_by=created_by,
            status=status or "active",
            project_metadata=project_metadata or {},
            module_config=module_config or {},
            created_at=now,
            updated_at=now
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        data = self.model_dump()
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectModel':
        """Create model instance from DynamoDB data"""
        return cls(**data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "id": self.pk,  # Return as 'id' for API consistency
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "status": self.status,
            "project_metadata": self.project_metadata,
            "module_config": self.module_config,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields and set updated_at timestamp"""
        for field, value in kwargs.items():
            if hasattr(self, field) and value is not None:
                setattr(self, field, value)
        
        # Always update the timestamp
        self.updated_at = datetime.utcnow().isoformat() 