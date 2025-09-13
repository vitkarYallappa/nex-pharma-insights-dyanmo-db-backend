"""
Insight Comment Model - Matches SQLAlchemy schema structure
Handles insight comment data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config.table_configs.insight_comment_table import InsightCommentTableConfig
from app.config.settings import settings

class InsightCommentModel(BaseModel):
    """Insight comment model matching SQLAlchemy schema"""
    
    # SQLAlchemy: id (UUID) -> DynamoDB: pk (String)
    pk: str = Field(..., description="Comment ID (UUID as string)")
    
    # SQLAlchemy: insight_id (UUID) -> DynamoDB: insight_id (String)
    insight_id: str = Field(..., description="Insight ID reference (UUID as string)")
    
    # SQLAlchemy: comment_text (Text) -> DynamoDB: comment_text (String)
    comment_text: str = Field(..., description="Comment text")
    
    # SQLAlchemy: comment_type (String) -> DynamoDB: comment_type (String)
    comment_type: Optional[str] = Field(None, description="Comment type")
    
    # SQLAlchemy: created_at (DateTime) -> DynamoDB: created_at (String)
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    
    # SQLAlchemy: updated_at (DateTime) -> DynamoDB: updated_at (String)
    updated_at: Optional[str] = Field(None, description="Last update timestamp (ISO string)")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return InsightCommentTableConfig.get_table_name()
    
    @classmethod
    def create_new(cls, insight_id: str, comment_text: str, comment_type: Optional[str] = None) -> 'InsightCommentModel':
        """Create a new insight comment instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            insight_id=insight_id,
            comment_text=comment_text,
            comment_type=comment_type,
            created_at=now,
            updated_at=now
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        data = self.model_dump()
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InsightCommentModel':
        """Create model instance from DynamoDB data"""
        return cls(**data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "id": self.pk,  # Return as 'id' for API consistency
            "insight_id": self.insight_id,
            "comment_text": self.comment_text,
            "comment_type": self.comment_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields and set updated_at timestamp"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['pk', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow().isoformat()
    
    def update_comment_text(self, comment_text: str) -> None:
        """Update comment text"""
        self.comment_text = comment_text
        self.updated_at = datetime.utcnow().isoformat()
    
    def update_comment_type(self, comment_type: str) -> None:
        """Update comment type"""
        self.comment_type = comment_type
        self.updated_at = datetime.utcnow().isoformat() 