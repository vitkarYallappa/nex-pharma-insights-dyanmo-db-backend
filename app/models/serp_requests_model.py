"""
SERP Requests Model for DynamoDB serp_requests Table
Used by Stage 0 SERP agent for search request tracking and metadata
"""

from typing import Dict, Any, Optional, List
from app.models.base_model import BaseModel
from app.config.settings import settings
from app.config.table_configs.serp_requests_table import SerpRequestsTableConfig

class SerpRequestsModel(BaseModel):
    """SERP requests model for DynamoDB operations"""
    
    def __init__(self, **kwargs):
        # Required fields
        self.request_id: str = kwargs.get('request_id')
        self.query: str = kwargs.get('query')
        self.num_results: int = kwargs.get('num_results', 10)
        self.search_engine: str = kwargs.get('search_engine', 'google')
        self.language: str = kwargs.get('language', 'en')
        self.country: str = kwargs.get('country', 'US')
        self.status: str = kwargs.get('status', 'pending')
        
        # Optional fields with defaults
        self.total_results: Optional[int] = kwargs.get('total_results')
        self.successful_results: Optional[int] = kwargs.get('successful_results')
        self.failed_results: Optional[int] = kwargs.get('failed_results')
        self.storage_key: Optional[str] = kwargs.get('storage_key')
        self.created_at: str = kwargs.get('created_at')
        self.updated_at: str = kwargs.get('updated_at')
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name"""
        return SerpRequestsTableConfig.get_table_name()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SerpRequestsModel':
        """Create SerpRequestsModel from dictionary"""
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SerpRequestsModel to dictionary for DynamoDB"""
        data = {
            'request_id': self.request_id,
            'query': self.query,
            'num_results': self.num_results,
            'search_engine': self.search_engine,
            'language': self.language,
            'country': self.country,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        # Add optional fields if they exist
        if self.total_results is not None:
            data['total_results'] = self.total_results
        if self.successful_results is not None:
            data['successful_results'] = self.successful_results
        if self.failed_results is not None:
            data['failed_results'] = self.failed_results
        if self.storage_key:
            data['storage_key'] = self.storage_key
            
        return data
    
    @classmethod
    def create_new(cls, query: str, num_results: int = 10, search_engine: str = 'google',
                   language: str = 'en', country: str = 'US') -> 'SerpRequestsModel':
        """Create a new SERP request model with generated ID and timestamps"""
        request_id = cls.generate_id()
        now = cls.current_timestamp()
        
        return cls(
            request_id=request_id,
            query=query,
            num_results=num_results,
            search_engine=search_engine,
            language=language,
            country=country,
            status='pending',
            created_at=now,
            updated_at=now
        )
    
    def update_results(self, total_results: int, successful_results: int, failed_results: int, storage_key: str):
        """Update search results and set storage location"""
        self.total_results = total_results
        self.successful_results = successful_results
        self.failed_results = failed_results
        self.storage_key = storage_key
        self.updated_at = self.current_timestamp()
    
    def update_status(self, status: str):
        """Update request status"""
        self.status = status
        self.updated_at = self.current_timestamp()
    
    def update_fields(self, **kwargs):
        """Update request fields and set updated_at"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['request_id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = self.current_timestamp()
    
    def to_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        return {
            'request_id': self.request_id,
            'query': self.query,
            'num_results': self.num_results,
            'total_results': self.total_results,
            'successful_results': self.successful_results,
            'failed_results': self.failed_results,
            'search_engine': self.search_engine,
            'language': self.language,
            'country': self.country,
            'storage_key': self.storage_key,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        } 