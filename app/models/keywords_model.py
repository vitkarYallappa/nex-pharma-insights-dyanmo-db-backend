"""
Keywords Model - Matches SQLAlchemy schema structure
Handles keywords data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config.table_configs.keywords_table import KeywordsTableConfig
from app.config.settings import settings

class KeywordsModel(BaseModel):
    """Keywords model matching SQLAlchemy schema"""
    
    # SQLAlchemy: id (UUID) -> DynamoDB: pk (String)
    pk: str = Field(..., description="Keyword ID (UUID as string)")
    
    # SQLAlchemy: keyword (String) -> DynamoDB: keyword (String)
    keyword: str = Field(..., description="Keyword text")
    
    # SQLAlchemy: request_id (UUID) -> DynamoDB: request_id (String)
    request_id: str = Field(..., description="Request ID reference (UUID as string)")
    
    # SQLAlchemy: keyword_type (String) -> DynamoDB: keyword_type (String)
    keyword_type: Optional[str] = Field(None, description="Keyword type/category")
    
    # SQLAlchemy: created_at (DateTime) -> DynamoDB: created_at (String)
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    
    # SQLAlchemy: updated_at (DateTime) -> DynamoDB: updated_at (String)
    updated_at: Optional[str] = Field(None, description="Last update timestamp (ISO string)")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return KeywordsTableConfig.get_table_name()
    
    @classmethod
    def create_new(cls, keyword: str, request_id: str, keyword_type: Optional[str] = None) -> 'KeywordsModel':
        """Create a new keyword instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            keyword=keyword,
            request_id=request_id,
            keyword_type=keyword_type,
            created_at=now,
            updated_at=now
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        data = self.model_dump()
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KeywordsModel':
        """Create model instance from DynamoDB data"""
        return cls(**data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "id": self.pk,  # Return as 'id' for API consistency
            "keyword": self.keyword,
            "request_id": self.request_id,
            "keyword_type": self.keyword_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields and set updated_at timestamp"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['pk', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow().isoformat() 