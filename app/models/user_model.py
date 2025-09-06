"""
User Model for DynamoDB Users Table
"""

from typing import Dict, Any, Optional
from app.models.base_model import BaseModel
from app.config.settings import settings
from app.config.tables import TableNames

class UserModel(BaseModel):
    """User model for DynamoDB operations"""
    
    def __init__(self, **kwargs):
        # Required fields
        self.pk: str = kwargs.get('pk')
        self.user_id: str = kwargs.get('user_id')
        self.email: str = kwargs.get('email')
        self.name: str = kwargs.get('name')
        self.hashed_password: str = kwargs.get('hashed_password')
        
        # Optional fields with defaults
        self.is_active: bool = kwargs.get('is_active', True)
        self.role: str = kwargs.get('role', 'user')
        self.created_at: str = kwargs.get('created_at')
        self.updated_at: str = kwargs.get('updated_at')
        self.last_login: Optional[str] = kwargs.get('last_login')
        self.login_count: int = kwargs.get('login_count', 0)
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name"""
        return TableNames.get_users_table(settings.TABLE_ENVIRONMENT)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserModel':
        """Create UserModel from dictionary"""
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert UserModel to dictionary for DynamoDB"""
        data = {
            'pk': self.pk,
            'user_id': self.user_id,
            'email': self.email,
            'name': self.name,
            'hashed_password': self.hashed_password,
            'is_active': self.is_active,
            'role': self.role,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'login_count': self.login_count
        }
        
        # Add optional fields if they exist
        if self.last_login:
            data['last_login'] = self.last_login
            
        return data
    
    @classmethod
    def create_new(cls, email: str, name: str, hashed_password: str, 
                   is_active: bool = True, role: str = 'user') -> 'UserModel':
        """Create a new user model with generated ID and timestamps"""
        user_id = cls.generate_id()
        now = cls.current_timestamp()
        
        return cls(
            pk=user_id,
            user_id=user_id,
            email=email,
            name=name,
            hashed_password=hashed_password,
            is_active=is_active,
            role=role,
            created_at=now,
            updated_at=now,
            last_login=None,
            login_count=0
        )
    
    def update_last_login(self):
        """Update last login timestamp and increment login count"""
        self.last_login = self.current_timestamp()
        self.login_count += 1
        self.updated_at = self.current_timestamp()
    
    def update_fields(self, **kwargs):
        """Update user fields and set updated_at"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['pk', 'user_id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = self.current_timestamp()
    
    def to_response(self) -> Dict[str, Any]:
        """Convert to API response format (excluding sensitive data)"""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'name': self.name,
            'is_active': self.is_active,
            'role': self.role,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_login': self.last_login,
            'login_count': self.login_count
        }