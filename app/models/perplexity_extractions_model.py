"""
Perplexity Extractions Model for DynamoDB perplexity_extractions Table
Used by Stage 0 Perplexity agent for content extraction tracking
"""

from typing import Dict, Any, Optional
from app.models.base_model import BaseModel
from app.config.settings import settings
from app.config.table_configs.perplexity_extractions_table import PerplexityExtractionsTableConfig

class PerplexityExtractionsModel(BaseModel):
    """Perplexity extractions model for DynamoDB operations"""
    
    def __init__(self, **kwargs):
        # Required fields
        self.request_id: str = kwargs.get('request_id')
        self.status: str = kwargs.get('status', 'pending')
        
        # Optional fields with defaults
        self.total_urls: Optional[int] = kwargs.get('total_urls')
        self.successful_extractions: Optional[int] = kwargs.get('successful_extractions')
        self.failed_extractions: Optional[int] = kwargs.get('failed_extractions')
        self.storage_key: Optional[str] = kwargs.get('storage_key')
        self.created_at: str = kwargs.get('created_at')
        self.updated_at: str = kwargs.get('updated_at')
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name"""
        return PerplexityExtractionsTableConfig.get_table_name()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerplexityExtractionsModel':
        """Create PerplexityExtractionsModel from dictionary"""
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert PerplexityExtractionsModel to dictionary for DynamoDB"""
        data = {
            'request_id': self.request_id,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        # Add optional fields if they exist
        if self.total_urls is not None:
            data['total_urls'] = self.total_urls
        if self.successful_extractions is not None:
            data['successful_extractions'] = self.successful_extractions
        if self.failed_extractions is not None:
            data['failed_extractions'] = self.failed_extractions
        if self.storage_key:
            data['storage_key'] = self.storage_key
            
        return data
    
    @classmethod
    def create_new(cls, request_id: str) -> 'PerplexityExtractionsModel':
        """Create a new perplexity extraction model with timestamps"""
        now = cls.current_timestamp()
        
        return cls(
            request_id=request_id,
            status='pending',
            created_at=now,
            updated_at=now
        )
    
    def update_extraction_results(self, total_urls: int, successful_extractions: int, 
                                failed_extractions: int, storage_key: str):
        """Update extraction results and set storage location"""
        self.total_urls = total_urls
        self.successful_extractions = successful_extractions
        self.failed_extractions = failed_extractions
        self.storage_key = storage_key
        self.updated_at = self.current_timestamp()
    
    def update_status(self, status: str):
        """Update extraction status"""
        self.status = status
        self.updated_at = self.current_timestamp()
    
    def update_fields(self, **kwargs):
        """Update extraction fields and set updated_at"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['request_id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = self.current_timestamp()
    
    def to_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        return {
            'request_id': self.request_id,
            'total_urls': self.total_urls,
            'successful_extractions': self.successful_extractions,
            'failed_extractions': self.failed_extractions,
            'storage_key': self.storage_key,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        } 