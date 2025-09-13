"""
Content Relevance Model - Matches SQLAlchemy schema structure
Handles content relevance data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from decimal import Decimal

from app.config.table_configs.content_relevance_table import ContentRelevanceTableConfig
from app.config.settings import settings

class ContentRelevanceModel(BaseModel):
    """Content relevance model for DynamoDB operations"""
    
    # Primary key - relevance_id (UUID) -> pk (String)
    pk: str = Field(..., description="Relevance ID (UUID as string)")
    
    # URL ID reference - url_id (UUID) -> url_id (String)
    url_id: str = Field(..., description="URL ID reference (UUID as string)")
    
    # Content repository reference - content_id (UUID) -> content_id (String)
    content_id: str = Field(..., description="Content repository ID reference (UUID as string)")
    
    # Relevance analysis text - relevance_text (String) -> relevance_text (String)
    relevance_text: str = Field(..., description="Relevance analysis text")
    
    # Relevance score - relevance_score (str) -> relevance_score (Number)
    relevance_score: str = Field(..., description="Relevance score (0.0 to 1.0)")
    
    # Relevance flag - is_relevant (Boolean) -> is_relevant (Boolean)
    is_relevant: bool = Field(..., description="Whether content is relevant")
    
    # File path - relevance_content_file_path (String) -> relevance_content_file_path (String)
    relevance_content_file_path: Optional[str] = Field(None, description="Relevance content file path")
    
    # Relevance category - relevance_category (String) -> relevance_category (String)
    relevance_category: str = Field(..., description="Relevance category")
    
    # Confidence score - confidence_score (str) -> confidence_score (Number)
    confidence_score: str = Field(..., description="Confidence score (0.0 to 1.0)")
    
    # Version - version (Integer) -> version (Number)
    version: Optional[int] = Field(None, description="Version number")
    
    # Canonical flag - is_canonical (Boolean) -> is_canonical (Boolean)
    is_canonical: Optional[bool] = Field(None, description="Canonical status")
    
    # Preferred choice flag - preferred_choice (Boolean) -> preferred_choice (Boolean)
    preferred_choice: Optional[bool] = Field(None, description="Preferred choice flag")
    
    # Timestamps - created_at (DateTime) -> created_at (String)
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    
    # Creator - created_by (String) -> created_by (String)
    created_by: str = Field(..., description="Creator identifier")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return ContentRelevanceTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
    
    @classmethod
    def create_new(cls, url_id: str, content_id: str, relevance_text: str,
                   relevance_score: str, is_relevant: bool, relevance_category: str,
                   confidence_score: str, relevance_content_file_path: Optional[str] = None,
                   version: Optional[int] = None, is_canonical: Optional[bool] = None,
                   preferred_choice: Optional[bool] = None,
                   created_by: str = "system") -> 'ContentRelevanceModel':
        """Create a new content relevance instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            url_id=url_id,
            content_id=content_id,
            relevance_text=relevance_text,
            relevance_score=relevance_score,
            is_relevant=is_relevant,
            relevance_content_file_path=relevance_content_file_path,
            relevance_category=relevance_category,
            confidence_score=confidence_score,
            version=version or 1,
            is_canonical=is_canonical if is_canonical is not None else True,
            preferred_choice=preferred_choice if preferred_choice is not None else True,
            created_at=now,
            created_by=created_by
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        data = self.model_dump()
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentRelevanceModel':
        """Create model instance from DynamoDB data"""
        # Convert Decimal values to strings for Pydantic validation
        converted_data = data.copy()
        if 'confidence_score' in converted_data and isinstance(converted_data['confidence_score'], Decimal):
            converted_data['confidence_score'] = str(converted_data['confidence_score'])
        if 'relevance_score' in converted_data and isinstance(converted_data['relevance_score'], Decimal):
            converted_data['relevance_score'] = str(converted_data['relevance_score'])
        return cls(**converted_data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "relevance_id": self.pk,  # Return as 'relevance_id' for API consistency
            "url_id": self.url_id,
            "content_id": self.content_id,
            "relevance_text": self.relevance_text,
            "relevance_score": self.relevance_score,
            "is_relevant": self.is_relevant,
            "relevance_content_file_path": self.relevance_content_file_path,
            "relevance_category": self.relevance_category,
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
            if hasattr(self, key) and key not in ['pk', 'created_at', 'created_by']:
                setattr(self, key, value)
    
    def update_relevance_analysis(self, relevance_text: str, relevance_score: str,
                                is_relevant: bool, confidence_score: str,
                                relevance_category: Optional[str] = None):
        """Update relevance analysis data"""
        self.relevance_text = relevance_text
        self.relevance_score = relevance_score
        self.is_relevant = is_relevant
        self.confidence_score = confidence_score
        if relevance_category:
            self.relevance_category = relevance_category
    
    def set_file_path(self, file_path: str):
        """Set relevance content file path"""
        self.relevance_content_file_path = file_path
    
    def set_version(self, version: int):
        """Set version number"""
        self.version = version
    
    def set_canonical_status(self, is_canonical: bool, preferred_choice: Optional[bool] = None):
        """Set canonical status and preferred choice"""
        self.is_canonical = is_canonical
        if preferred_choice is not None:
            self.preferred_choice = preferred_choice
    
    def is_high_relevance(self) -> bool:
        """Check if content has high relevance score"""
        return self.relevance_score >= 0.7 and self.is_relevant
    
    def is_low_confidence(self) -> bool:
        """Check if confidence score is low"""
        return self.confidence_score < 0.5
    
    def get_relevance_summary(self) -> Dict[str, Any]:
        """Get a summary of relevance analysis"""
        return {
            "relevance_score": self.relevance_score,
            "confidence_score": self.confidence_score,
            "is_relevant": self.is_relevant,
            "category": self.relevance_category,
            "high_relevance": self.is_high_relevance(),
            "low_confidence": self.is_low_confidence()
        } 