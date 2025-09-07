"""
Global Base URLs Model - Matches SQLAlchemy schema structure
Handles global base URLs data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config.table_configs.global_base_urls_table import GlobalBaseUrlsTableConfig
from app.config.settings import settings

class GlobalBaseUrlsModel(BaseModel):
    """Global base URLs model matching SQLAlchemy schema"""
    
    # SQLAlchemy: id (UUID) -> DynamoDB: pk (String)
    pk: str = Field(..., description="URL ID (UUID as string)")
    
    # SQLAlchemy: url (String) -> DynamoDB: url (String)
    url: str = Field(..., description="Base URL")
    
    # SQLAlchemy: source_name (String) -> DynamoDB: source_name (String)
    source_name: Optional[str] = Field(None, description="Source name")
    
    # SQLAlchemy: source_type (String) -> DynamoDB: source_type (String)
    source_type: Optional[str] = Field(None, description="Source type")
    
    # SQLAlchemy: country_region (String) -> DynamoDB: country_region (String)
    country_region: Optional[str] = Field(None, description="Country/region")
    
    # SQLAlchemy: is_active (Boolean) -> DynamoDB: is_active (Boolean)
    is_active: bool = Field(True, description="Active status")
    
    # SQLAlchemy: url_metadata (JSON) -> DynamoDB: url_metadata (Map)
    url_metadata: Optional[Dict[str, Any]] = Field(None, description="URL metadata JSON")
    
    # SQLAlchemy: created_at (DateTime) -> DynamoDB: created_at (String)
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    
    # SQLAlchemy: updated_at (DateTime) -> DynamoDB: updated_at (String)
    updated_at: Optional[str] = Field(None, description="Last update timestamp (ISO string)")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return GlobalBaseUrlsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
    
    @classmethod
    def create_new(cls, url: str, source_name: Optional[str] = None, source_type: Optional[str] = None,
                   country_region: Optional[str] = None, is_active: bool = True,
                   url_metadata: Optional[Dict[str, Any]] = None) -> 'GlobalBaseUrlsModel':
        """Create a new global base URL instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            url=url,
            source_name=source_name,
            source_type=source_type,
            country_region=country_region,
            is_active=is_active,
            url_metadata=url_metadata or {},
            created_at=now,
            updated_at=now
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        data = self.model_dump()
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GlobalBaseUrlsModel':
        """Create model instance from DynamoDB data"""
        return cls(**data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "id": self.pk,  # Return as 'id' for API consistency
            "url": self.url,
            "source_name": self.source_name,
            "source_type": self.source_type,
            "country_region": self.country_region,
            "is_active": self.is_active,
            "url_metadata": self.url_metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields and set updated_at timestamp"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['pk', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow().isoformat() 