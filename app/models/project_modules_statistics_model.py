"""
Project Modules Statistics Model - Matches SQLAlchemy schema structure
Handles project modules statistics data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config.table_configs.project_modules_statistics_table import ProjectModulesStatisticsTableConfig
from app.config.settings import settings

class ProjectModulesStatisticsModel(BaseModel):
    """Project modules statistics model matching SQLAlchemy schema"""
    
    # SQLAlchemy: id (UUID) -> DynamoDB: pk (String)
    pk: str = Field(..., description="Statistics ID (UUID as string)")
    
    # SQLAlchemy: project_id (UUID) -> DynamoDB: project_id (String)
    project_id: str = Field(..., description="Project ID reference (UUID as string)")
    
    # SQLAlchemy: total_insights (Integer) -> DynamoDB: total_insights (Number)
    total_insights: Optional[int] = Field(None, description="Total insights count")
    
    # SQLAlchemy: total_implication (Integer) -> DynamoDB: total_implication (Number)
    total_implication: Optional[int] = Field(None, description="Total implication count")
    
    # SQLAlchemy: created_at (DateTime) -> DynamoDB: created_at (String)
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    
    # SQLAlchemy: updated_at (DateTime) -> DynamoDB: updated_at (String)
    updated_at: Optional[str] = Field(None, description="Last update timestamp (ISO string)")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return ProjectModulesStatisticsTableConfig.get_table_name()
    
    @classmethod
    def create_new(cls, project_id: str, total_insights: Optional[int] = None,
                   total_implication: Optional[int] = None) -> 'ProjectModulesStatisticsModel':
        """Create a new project modules statistics instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            project_id=project_id,
            total_insights=total_insights,
            total_implication=total_implication,
            created_at=now,
            updated_at=now
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        data = self.model_dump()
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectModulesStatisticsModel':
        """Create model instance from DynamoDB data"""
        return cls(**data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "id": self.pk,  # Return as 'id' for API consistency
            "project_id": self.project_id,
            "total_insights": self.total_insights,
            "total_implication": self.total_implication,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields and set updated_at timestamp"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['pk', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow().isoformat() 