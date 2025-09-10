"""
Pipeline States Model for DynamoDB pipeline_states Table
Used by Stage 0 Orchestrator agent for pipeline orchestration state tracking
"""

from typing import Dict, Any, Optional, List
from app.models.base_model import BaseModel
from app.config.settings import settings
from app.config.table_configs.pipeline_states_table import PipelineStatesTableConfig

class PipelineStatesModel(BaseModel):
    """Pipeline states model for DynamoDB operations"""
    
    def __init__(self, **kwargs):
        # Required fields
        self.request_id: str = kwargs.get('request_id')
        self.status: str = kwargs.get('status', 'pending')
        self.current_stage: str = kwargs.get('current_stage', 'initialization')
        self.progress_percentage: int = kwargs.get('progress_percentage', 0)
        
        # Stage completion flags
        self.search_completed: bool = kwargs.get('search_completed', False)
        self.extraction_completed: bool = kwargs.get('extraction_completed', False)
        self.aggregation_completed: bool = kwargs.get('aggregation_completed', False)
        
        # Metrics
        self.urls_found: Optional[int] = kwargs.get('urls_found')
        self.content_extracted: Optional[int] = kwargs.get('content_extracted')
        self.content_failed: Optional[int] = kwargs.get('content_failed')
        
        # Timestamps
        self.started_at: str = kwargs.get('started_at')
        self.search_started_at: Optional[str] = kwargs.get('search_started_at')
        self.extraction_started_at: Optional[str] = kwargs.get('extraction_started_at')
        self.completed_at: Optional[str] = kwargs.get('completed_at')
        
        # Messages
        self.errors: List[str] = kwargs.get('errors', [])
        self.warnings: List[str] = kwargs.get('warnings', [])
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name"""
        return PipelineStatesTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineStatesModel':
        """Create PipelineStatesModel from dictionary"""
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert PipelineStatesModel to dictionary for DynamoDB"""
        data = {
            'request_id': self.request_id,
            'status': self.status,
            'current_stage': self.current_stage,
            'progress_percentage': self.progress_percentage,
            'search_completed': self.search_completed,
            'extraction_completed': self.extraction_completed,
            'aggregation_completed': self.aggregation_completed,
            'started_at': self.started_at,
            'errors': self.errors,
            'warnings': self.warnings
        }
        
        # Add optional fields if they exist
        if self.urls_found is not None:
            data['urls_found'] = self.urls_found
        if self.content_extracted is not None:
            data['content_extracted'] = self.content_extracted
        if self.content_failed is not None:
            data['content_failed'] = self.content_failed
        if self.search_started_at:
            data['search_started_at'] = self.search_started_at
        if self.extraction_started_at:
            data['extraction_started_at'] = self.extraction_started_at
        if self.completed_at:
            data['completed_at'] = self.completed_at
            
        return data
    
    @classmethod
    def create_new(cls, request_id: str) -> 'PipelineStatesModel':
        """Create a new pipeline state model with initial values"""
        now = cls.current_timestamp()
        
        return cls(
            request_id=request_id,
            status='pending',
            current_stage='initialization',
            progress_percentage=0,
            search_completed=False,
            extraction_completed=False,
            aggregation_completed=False,
            started_at=now,
            errors=[],
            warnings=[]
        )
    
    def start_search_stage(self):
        """Mark search stage as started"""
        self.current_stage = 'searching'
        self.status = 'searching'
        self.search_started_at = self.current_timestamp()
        self.progress_percentage = 10
    
    def complete_search_stage(self, urls_found: int):
        """Mark search stage as completed"""
        self.search_completed = True
        self.urls_found = urls_found
        self.progress_percentage = 30
    
    def start_extraction_stage(self):
        """Mark extraction stage as started"""
        self.current_stage = 'extracting'
        self.status = 'extracting'
        self.extraction_started_at = self.current_timestamp()
        self.progress_percentage = 40
    
    def update_extraction_progress(self, content_extracted: int, content_failed: int):
        """Update extraction progress"""
        self.content_extracted = content_extracted
        self.content_failed = content_failed
        total_processed = content_extracted + content_failed
        if self.urls_found and self.urls_found > 0:
            extraction_progress = min(50, int((total_processed / self.urls_found) * 50))
            self.progress_percentage = 40 + extraction_progress
    
    def complete_extraction_stage(self):
        """Mark extraction stage as completed"""
        self.extraction_completed = True
        self.progress_percentage = 90
    
    def start_aggregation_stage(self):
        """Mark aggregation stage as started"""
        self.current_stage = 'aggregating'
        self.status = 'aggregating'
        self.progress_percentage = 95
    
    def complete_pipeline(self, final_status: str = 'completed'):
        """Mark entire pipeline as completed"""
        self.aggregation_completed = True
        self.status = final_status
        self.current_stage = 'completed'
        self.progress_percentage = 100
        self.completed_at = self.current_timestamp()
    
    def add_error(self, error_message: str):
        """Add an error message"""
        self.errors.append(error_message)
    
    def add_warning(self, warning_message: str):
        """Add a warning message"""
        self.warnings.append(warning_message)
    
    def update_status(self, status: str, current_stage: str = None):
        """Update pipeline status and optionally current stage"""
        self.status = status
        if current_stage:
            self.current_stage = current_stage
    
    def to_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        return {
            'request_id': self.request_id,
            'status': self.status,
            'current_stage': self.current_stage,
            'progress_percentage': self.progress_percentage,
            'search_completed': self.search_completed,
            'extraction_completed': self.extraction_completed,
            'aggregation_completed': self.aggregation_completed,
            'urls_found': self.urls_found,
            'content_extracted': self.content_extracted,
            'content_failed': self.content_failed,
            'started_at': self.started_at,
            'search_started_at': self.search_started_at,
            'extraction_started_at': self.extraction_started_at,
            'completed_at': self.completed_at,
            'errors': self.errors,
            'warnings': self.warnings
        } 