"""
Perplexity Content Model for DynamoDB perplexity_content Table
Used by Stage 0 Perplexity agent for individual content extraction results
"""

from typing import Dict, Any, Optional
from app.models.base_model import BaseModel
from app.config.settings import settings
from app.config.table_configs.perplexity_content_table import PerplexityContentTableConfig
import hashlib

class PerplexityContentModel(BaseModel):
    """Perplexity content model for DynamoDB operations"""
    
    def __init__(self, **kwargs):
        # Required fields
        self.content_id: str = kwargs.get('content_id')
        self.request_id: str = kwargs.get('request_id')
        self.url: str = kwargs.get('url')
        self.title: str = kwargs.get('title', '')
        
        # Optional fields with defaults
        self.word_count: Optional[int] = kwargs.get('word_count')
        self.extraction_confidence: Optional[str] = kwargs.get('extraction_confidence')
        self.content_type: str = kwargs.get('content_type', 'article')
        self.language: str = kwargs.get('language', 'en')
        self.created_at: str = kwargs.get('created_at')
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name"""
        return PerplexityContentTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerplexityContentModel':
        """Create PerplexityContentModel from dictionary"""
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert PerplexityContentModel to dictionary for DynamoDB"""
        data = {
            'content_id': self.content_id,
            'request_id': self.request_id,
            'url': self.url,
            'title': self.title,
            'content_type': self.content_type,
            'language': self.language,
            'created_at': self.created_at
        }
        
        # Add optional fields if they exist
        if self.word_count is not None:
            data['word_count'] = self.word_count
        if self.extraction_confidence is not None:
            data['extraction_confidence'] = self.extraction_confidence
            
        return data
    
    @classmethod
    def create_new(cls, request_id: str, url: str, title: str = '', word_count: Optional[int] = None,
                   extraction_confidence: Optional[str] = None, content_type: str = 'article',
                   language: str = 'en') -> 'PerplexityContentModel':
        """Create a new perplexity content model with generated content_id and timestamp"""
        # Generate content_id as {request_id}_{url_hash}
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        content_id = f"{request_id}_{url_hash}"
        now = cls.current_timestamp()
        
        return cls(
            content_id=content_id,
            request_id=request_id,
            url=url,
            title=title,
            word_count=word_count,
            extraction_confidence=extraction_confidence,
            content_type=content_type,
            language=language,
            created_at=now
        )
    
    def update_content_metrics(self, word_count: int, extraction_confidence: str):
        """Update content metrics"""
        self.word_count = word_count
        self.extraction_confidence = extraction_confidence
    
    def update_fields(self, **kwargs):
        """Update content fields"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['content_id', 'request_id', 'created_at']:
                setattr(self, key, value)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        return {
            'content_id': self.content_id,
            'request_id': self.request_id,
            'url': self.url,
            'title': self.title,
            'word_count': self.word_count,
            'extraction_confidence': self.extraction_confidence,
            'content_type': self.content_type,
            'language': self.language,
            'created_at': self.created_at
        } 