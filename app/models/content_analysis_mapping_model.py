"""
Content Analysis Mapping Model - Matches SQLAlchemy schema structure
Handles content analysis mapping data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config.table_configs.content_analysis_mapping_table import ContentAnalysisMappingTableConfig
from app.config.settings import settings

class ContentAnalysisMappingModel(BaseModel):
    """Content analysis mapping model matching SQLAlchemy schema"""
    
    # SQLAlchemy: mapping_id (UUID) -> DynamoDB: pk (String)
    pk: str = Field(..., description="Mapping ID (UUID as string)")
    
    # SQLAlchemy: content_id (UUID) -> DynamoDB: content_id (String)
    content_id: str = Field(..., description="Content ID reference (UUID as string)")
    
    # SQLAlchemy: primary_summary_id (UUID) -> DynamoDB: primary_summary_id (String)
    primary_summary_id: Optional[str] = Field(None, description="Primary summary ID reference (UUID as string)")
    
    # SQLAlchemy: primary_insight_id (UUID) -> DynamoDB: primary_insight_id (String)
    primary_insight_id: Optional[str] = Field(None, description="Primary insight ID reference (UUID as string)")
    
    # SQLAlchemy: primary_implication_id (UUID) -> DynamoDB: primary_implication_id (String)
    primary_implication_id: Optional[str] = Field(None, description="Primary implication ID reference (UUID as string)")
    
    # SQLAlchemy: selection_strategy (String) -> DynamoDB: selection_strategy (String)
    selection_strategy: Optional[str] = Field(None, description="Selection strategy")
    
    # SQLAlchemy: selection_context (String) -> DynamoDB: selection_context (String)
    selection_context: Optional[str] = Field(None, description="Selection context")
    
    # SQLAlchemy: selected_by (String) -> DynamoDB: selected_by (String)
    selected_by: Optional[str] = Field(None, description="Selected by identifier")
    
    # SQLAlchemy: selected_at (DateTime) -> DynamoDB: selected_at (String)
    selected_at: Optional[str] = Field(None, description="Selection timestamp (ISO string)")
    
    # SQLAlchemy: version (Integer) -> DynamoDB: version (Number)
    version: Optional[int] = Field(None, description="Version number")
    
    # SQLAlchemy: is_current (Boolean) -> DynamoDB: is_current (Boolean)
    is_current: Optional[bool] = Field(None, description="Current flag")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return ContentAnalysisMappingTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
    
    @classmethod
    def create_new(cls, content_id: str, primary_summary_id: Optional[str] = None,
                   primary_insight_id: Optional[str] = None, primary_implication_id: Optional[str] = None,
                   selection_strategy: Optional[str] = None, selection_context: Optional[str] = None,
                   selected_by: Optional[str] = None, version: Optional[int] = None,
                   is_current: Optional[bool] = None) -> 'ContentAnalysisMappingModel':
        """Create a new content analysis mapping instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            content_id=content_id,
            primary_summary_id=primary_summary_id,
            primary_insight_id=primary_insight_id,
            primary_implication_id=primary_implication_id,
            selection_strategy=selection_strategy,
            selection_context=selection_context,
            selected_by=selected_by,
            selected_at=now,
            version=version if version is not None else 1,
            is_current=is_current if is_current is not None else True
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        data = self.model_dump()
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentAnalysisMappingModel':
        """Create model instance from DynamoDB data"""
        return cls(**data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "mapping_id": self.pk,  # Return as 'mapping_id' for API consistency
            "content_id": self.content_id,
            "primary_summary_id": self.primary_summary_id,
            "primary_insight_id": self.primary_insight_id,
            "primary_implication_id": self.primary_implication_id,
            "selection_strategy": self.selection_strategy,
            "selection_context": self.selection_context,
            "selected_by": self.selected_by,
            "selected_at": self.selected_at,
            "version": self.version,
            "is_current": self.is_current
        }
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['pk', 'selected_at']:
                setattr(self, key, value)
    
    def mark_as_current(self) -> None:
        """Mark mapping as current"""
        self.is_current = True
    
    def mark_as_outdated(self) -> None:
        """Mark mapping as outdated"""
        self.is_current = False
    
    def update_primary_summary(self, summary_id: str, strategy: Optional[str] = None,
                              context: Optional[str] = None, selected_by: Optional[str] = None) -> None:
        """Update primary summary selection"""
        self.primary_summary_id = summary_id
        if strategy:
            self.selection_strategy = strategy
        if context:
            self.selection_context = context
        if selected_by:
            self.selected_by = selected_by
        self.selected_at = datetime.utcnow().isoformat()
    
    def update_primary_insight(self, insight_id: str, strategy: Optional[str] = None,
                              context: Optional[str] = None, selected_by: Optional[str] = None) -> None:
        """Update primary insight selection"""
        self.primary_insight_id = insight_id
        if strategy:
            self.selection_strategy = strategy
        if context:
            self.selection_context = context
        if selected_by:
            self.selected_by = selected_by
        self.selected_at = datetime.utcnow().isoformat()
    
    def update_primary_implication(self, implication_id: str, strategy: Optional[str] = None,
                                  context: Optional[str] = None, selected_by: Optional[str] = None) -> None:
        """Update primary implication selection"""
        self.primary_implication_id = implication_id
        if strategy:
            self.selection_strategy = strategy
        if context:
            self.selection_context = context
        if selected_by:
            self.selected_by = selected_by
        self.selected_at = datetime.utcnow().isoformat()
    
    def increment_version(self) -> None:
        """Increment version number"""
        if self.version is None:
            self.version = 1
        else:
            self.version += 1 