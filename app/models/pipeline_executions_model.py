"""
Pipeline Executions Model for DynamoDB pipeline_executions Table
Used by Stage 0 Orchestrator agent for pipeline execution history and analytics
"""

from typing import Dict, Any, Optional
from app.models.base_model import BaseModel
from app.config.settings import settings
from app.config.table_configs.pipeline_executions_table import PipelineExecutionsTableConfig

class PipelineExecutionsModel(BaseModel):
    """Pipeline executions model for DynamoDB operations"""
    
    def __init__(self, **kwargs):
        # Required fields
        self.request_id: str = kwargs.get('request_id')
        self.original_query: str = kwargs.get('original_query')
        self.final_status: str = kwargs.get('final_status', 'pending')
        self.created_at: str = kwargs.get('created_at')
        
        # Optional fields with defaults
        self.total_urls: Optional[int] = kwargs.get('total_urls')
        self.content_extracted: Optional[int] = kwargs.get('content_extracted')
        self.processing_time: Optional[int] = kwargs.get('processing_time')  # in seconds
        self.storage_paths: Dict[str, str] = kwargs.get('storage_paths', {})
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name"""
        return PipelineExecutionsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineExecutionsModel':
        """Create PipelineExecutionsModel from dictionary"""
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert PipelineExecutionsModel to dictionary for DynamoDB"""
        data = {
            'request_id': self.request_id,
            'original_query': self.original_query,
            'final_status': self.final_status,
            'storage_paths': self.storage_paths,
            'created_at': self.created_at
        }
        
        # Add optional fields if they exist
        if self.total_urls is not None:
            data['total_urls'] = self.total_urls
        if self.content_extracted is not None:
            data['content_extracted'] = self.content_extracted
        if self.processing_time is not None:
            data['processing_time'] = self.processing_time
            
        return data
    
    @classmethod
    def create_new(cls, request_id: str, original_query: str) -> 'PipelineExecutionsModel':
        """Create a new pipeline execution model with initial values"""
        now = cls.current_timestamp()
        
        return cls(
            request_id=request_id,
            original_query=original_query,
            final_status='pending',
            storage_paths={},
            created_at=now
        )
    
    def update_execution_results(self, total_urls: int, content_extracted: int, 
                               processing_time: int, final_status: str):
        """Update execution results"""
        self.total_urls = total_urls
        self.content_extracted = content_extracted
        self.processing_time = processing_time
        self.final_status = final_status
    
    def add_storage_path(self, path_type: str, path: str):
        """Add a storage path for a specific type"""
        self.storage_paths[path_type] = path
    
    def update_storage_paths(self, storage_paths: Dict[str, str]):
        """Update all storage paths"""
        self.storage_paths.update(storage_paths)
    
    def update_final_status(self, final_status: str):
        """Update final execution status"""
        self.final_status = final_status
    
    def update_fields(self, **kwargs):
        """Update execution fields"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['request_id', 'created_at']:
                setattr(self, key, value)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        return {
            'request_id': self.request_id,
            'original_query': self.original_query,
            'total_urls': self.total_urls,
            'content_extracted': self.content_extracted,
            'processing_time': self.processing_time,
            'final_status': self.final_status,
            'storage_paths': self.storage_paths,
            'created_at': self.created_at
        } 