"""
Content Repository Metadata Model - Handles metadata for content repository entries
Stores additional metadata information for content repository data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config.table_configs.content_repository_metadata_table import ContentRepositoryMetadataTableConfig
from app.config.settings import settings

class ContentRepositoryMetadataModel(BaseModel):
    """Content repository metadata model for DynamoDB operations"""
    
    # Primary key - metadata_id (UUID) -> pk (String)
    pk: str = Field(..., description="Metadata ID (UUID as string)")
    
    # Content repository reference - content_id (UUID) -> content_id (String)
    content_id: str = Field(..., description="Content repository ID reference (UUID as string)")
    
    # Request ID reference - request_id (UUID) -> request_id (String)
    request_id: str = Field(..., description="Request ID reference (UUID as string)")
    
    # Project ID reference - project_id (UUID) -> project_id (String)
    project_id: str = Field(..., description="Project ID reference (UUID as string)")
    
    # Metadata type - metadata_type (String) -> metadata_type (String)
    metadata_type: str = Field(..., description="Type of metadata (e.g., extraction_info, processing_info, quality_metrics)")
    
    # Metadata key - metadata_key (String) -> metadata_key (String)
    metadata_key: str = Field(..., description="Metadata key identifier")
    
    # Metadata value - metadata_value (String) -> metadata_value (String)
    metadata_value: str = Field(..., description="Metadata value (stored as string)")
    
    # Data type - data_type (String) -> data_type (String)
    data_type: str = Field(..., description="Data type of the value (string, number, boolean, json)")
    
    # Searchable flag - is_searchable (Boolean) -> is_searchable (Boolean)
    is_searchable: Optional[bool] = Field(None, description="Whether this metadata is searchable")
    
    # Timestamps - created_at (DateTime) -> created_at (String)
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    
    # Updated timestamp - updated_at (DateTime) -> updated_at (String)
    updated_at: Optional[str] = Field(None, description="Last update timestamp (ISO string)")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return ContentRepositoryMetadataTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
    
    @classmethod
    def create_new(cls, content_id: str, request_id: str, project_id: str, 
                   metadata_type: str, metadata_key: str, metadata_value: str,
                   data_type: str, is_searchable: Optional[bool] = None) -> 'ContentRepositoryMetadataModel':
        """Create a new content repository metadata instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            content_id=content_id,
            request_id=request_id,
            project_id=project_id,
            metadata_type=metadata_type,
            metadata_key=metadata_key,
            metadata_value=metadata_value,
            data_type=data_type,
            is_searchable=is_searchable,
            created_at=now,
            updated_at=now
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        data = self.model_dump()
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentRepositoryMetadataModel':
        """Create model instance from DynamoDB data"""
        return cls(**data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "metadata_id": self.pk,  # Return as 'metadata_id' for API consistency
            "content_id": self.content_id,
            "request_id": self.request_id,
            "project_id": self.project_id,
            "metadata_type": self.metadata_type,
            "metadata_key": self.metadata_key,
            "metadata_value": self.metadata_value,
            "data_type": self.data_type,
            "is_searchable": self.is_searchable,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields and set updated_at timestamp"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['pk', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow().isoformat()
    
    def get_typed_value(self) -> Any:
        """Get the metadata value converted to its proper data type"""
        if self.data_type == "number":
            try:
                # Try integer first, then str
                if '.' in self.metadata_value:
                    return str(self.metadata_value)
                else:
                    return int(self.metadata_value)
            except ValueError:
                return self.metadata_value
        elif self.data_type == "boolean":
            return self.metadata_value.lower() in ('true', '1', 'yes', 'on')
        elif self.data_type == "json":
            try:
                import json
                return json.loads(self.metadata_value)
            except (json.JSONDecodeError, ValueError):
                return self.metadata_value
        else:  # string or unknown type
            return self.metadata_value
    
    def set_typed_value(self, value: Any) -> None:
        """Set the metadata value from a typed value"""
        if isinstance(value, (int, str)):
            self.metadata_value = str(value)
            self.data_type = "number"
        elif isinstance(value, bool):
            self.metadata_value = str(value).lower()
            self.data_type = "boolean"
        elif isinstance(value, (dict, list)):
            import json
            self.metadata_value = json.dumps(value)
            self.data_type = "json"
        else:
            self.metadata_value = str(value)
            self.data_type = "string" 