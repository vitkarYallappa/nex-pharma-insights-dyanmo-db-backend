"""
Content Implication Model - Matches SQLAlchemy schema structure
Handles content implication data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from decimal import Decimal

from app.config.table_configs.content_implication_table import ContentImplicationTableConfig
from app.config.settings import settings

class ContentImplicationModel(BaseModel):
    """Content implication model matching SQLAlchemy schema"""
    
    # SQLAlchemy: implication_id (UUID) -> DynamoDB: pk (String)
    pk: str = Field(..., description="Implication ID (UUID as string)")
    
    # SQLAlchemy: url_id (UUID) -> DynamoDB: url_id (String)
    url_id: str = Field(..., description="URL ID reference (UUID as string)")
    
    # SQLAlchemy: content_id (UUID) -> DynamoDB: content_id (String)
    content_id: str = Field(..., description="Content ID reference (UUID as string)")
    
    # SQLAlchemy: implication_text (String) -> DynamoDB: implication_text (String)
    implication_text: str = Field(..., description="Implication text")
    
    # SQLAlchemy: implication_content_file_path (String) -> DynamoDB: implication_content_file_path (String)
    implication_content_file_path: Optional[str] = Field(None, description="Implication content file path")
    
    # SQLAlchemy: implication_type (String) -> DynamoDB: implication_type (String)
    implication_type: Optional[str] = Field(None, description="Implication type")
    
    # SQLAlchemy: priority_level (String) -> DynamoDB: priority_level (String)
    priority_level: Optional[str] = Field(None, description="Priority level")
    
    # SQLAlchemy: confidence_score (Numeric) -> DynamoDB: confidence_score (Number)
    confidence_score: Optional[str] = Field(None, description="Confidence score")
    
    # SQLAlchemy: version (Integer) -> DynamoDB: version (Number)
    version: Optional[int] = Field(None, description="Version number")
    
    # SQLAlchemy: is_canonical (Boolean) -> DynamoDB: is_canonical (Boolean)
    is_canonical: Optional[bool] = Field(None, description="Canonical flag")
    
    # SQLAlchemy: preferred_choice (Boolean) -> DynamoDB: preferred_choice (Boolean)
    preferred_choice: Optional[bool] = Field(None, description="Preferred choice flag")
    
    # SQLAlchemy: created_at (DateTime) -> DynamoDB: created_at (String)
    created_at: Optional[str] = Field(None, description="Creation timestamp (ISO string)")
    
    # SQLAlchemy: created_by (String) -> DynamoDB: created_by (String)
    created_by: Optional[str] = Field(None, description="Creator identifier")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return ContentImplicationTableConfig.get_table_name()
    
    @classmethod
    def create_new(cls, url_id: str, content_id: str, implication_text: str,
                   implication_content_file_path: Optional[str] = None, implication_type: Optional[str] = None,
                   priority_level: Optional[str] = None, confidence_score: Optional[str] = None,
                   version: Optional[int] = None, is_canonical: Optional[bool] = None,
                   preferred_choice: Optional[bool] = None, created_by: Optional[str] = None) -> 'ContentImplicationModel':
        """Create a new content implication instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            url_id=url_id,
            content_id=content_id,
            implication_text=implication_text,
            implication_content_file_path=implication_content_file_path,
            implication_type=implication_type,
            priority_level=priority_level,
            confidence_score=confidence_score,
            version=version if version is not None else 1,
            is_canonical=is_canonical,
            preferred_choice=preferred_choice,
            created_at=now,
            created_by=created_by
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        data = self.model_dump()
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentImplicationModel':
        """Create model instance from DynamoDB data"""
        # Convert Decimal values to strings for Pydantic validation
        converted_data = data.copy()
        if 'confidence_score' in converted_data and isinstance(converted_data['confidence_score'], Decimal):
            converted_data['confidence_score'] = str(converted_data['confidence_score'])
        return cls(**converted_data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "implication_id": self.pk,  # Return as 'implication_id' for API consistency
            "url_id": self.url_id,
            "content_id": self.content_id,
            "implication_text": self.implication_text,
            "implication_content_file_path": self.implication_content_file_path,
            "implication_type": self.implication_type,
            "priority_level": self.priority_level,
            "confidence_score": self.confidence_score,
            "version": self.version,
            "is_canonical": self.is_canonical,
            "preferred_choice": self.preferred_choice,
            "created_at": self.created_at,
            "created_by": self.created_by
        }
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['pk', 'created_at']:
                setattr(self, key, value)
    
    def mark_as_canonical(self) -> None:
        """Mark implication as canonical"""
        self.is_canonical = True
    
    def mark_as_preferred(self) -> None:
        """Mark implication as preferred choice"""
        self.preferred_choice = True
    
    def update_confidence(self, score: str) -> None:
        """Update confidence score"""
        self.confidence_score = score
    
    def update_type(self, implication_type: str) -> None:
        """Update implication type"""
        self.implication_type = implication_type
    
    def update_priority(self, priority_level: str) -> None:
        """Update priority level"""
        self.priority_level = priority_level
    
    def increment_version(self) -> None:
        """Increment version number"""
        if self.version is None:
            self.version = 1
        else:
            self.version += 1 