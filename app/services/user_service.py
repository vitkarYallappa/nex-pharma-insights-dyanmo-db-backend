"""
Simplified User Service - Works with UserModel and simplified repository
"""

from typing import List, Optional
from passlib.context import CryptContext
from app.repositories.user_repository import UserRepository
from app.models.user_model import UserModel
from app.core.logging import get_logger
from app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException
)

logger = get_logger("user_service")

class UserService:
    """Simplified user service with essential operations"""
    
    def __init__(self):
        self.user_repository = UserRepository()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.logger = logger
    
    async def create_user(self, email: str, name: str, password: str, 
                         is_active: bool = True, role: str = 'user') -> UserModel:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = await self.user_repository.find_user_by_email(email)
            if existing_user:
                raise UserAlreadyExistsException(f"User with email {email} already exists")
            
            # Create user model
            user_model = UserModel.create_new(
                email=email,
                name=name,
                hashed_password=self.pwd_context.hash(password),
                is_active=is_active,
                role=role
            )
            
            # Save to database
            created_user = await self.user_repository.create(user_model)
            self.logger.info(f"User created: {email}")
            return created_user
            
        except UserAlreadyExistsException:
            raise
        except Exception as e:
            self.logger.error(f"Create user failed: {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> UserModel:
        """Get user by ID"""
        try:
            user = await self.user_repository.find_user_by_id(user_id)
            if not user:
                raise UserNotFoundException(f"User with ID {user_id} not found")
            
            self.logger.info(f"User found: {user_id}")
            return user
            
        except UserNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Get user failed: {str(e)}")
            raise
    
    async def get_user_by_email(self, email: str) -> UserModel:
        """Get user by email"""
        try:
            user = await self.user_repository.find_user_by_email(email)
            if not user:
                raise UserNotFoundException(f"User with email {email} not found")
            
            self.logger.info(f"User found: {email}")
            return user
            
        except UserNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Get user by email failed: {str(e)}")
            raise
    
    async def get_all_users(self, is_active: Optional[bool] = None, 
                           role: Optional[str] = None, 
                           limit: Optional[int] = None) -> List[UserModel]:
        """Get all users with optional filters"""
        try:
            users = await self.user_repository.get_all_users(
                is_active=is_active, 
                role=role, 
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(users)} users")
            return users
            
        except Exception as e:
            self.logger.error(f"Get all users failed: {str(e)}")
            raise