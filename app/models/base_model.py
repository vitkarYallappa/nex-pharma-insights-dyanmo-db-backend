"""
Base Model for DynamoDB Operations
Provides common functionality for all models
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class BaseModel(ABC):
    """Base model class with common DynamoDB functionality"""
    
    @classmethod
    def generate_id(cls) -> str:
        """Generate a unique ID"""
        return str(uuid.uuid4())
    
    @classmethod
    def current_timestamp(cls) -> str:
        """Get current timestamp in ISO format"""
        return datetime.utcnow().isoformat()
    
    @classmethod
    @abstractmethod
    def table_name(cls) -> str:
        """Return the DynamoDB table name for this model"""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model instance from dictionary"""
        pass
    
    def update_timestamp(self):
        """Update the updated_at timestamp if it exists"""
        if hasattr(self, 'updated_at'):
            self.updated_at = self.current_timestamp()
