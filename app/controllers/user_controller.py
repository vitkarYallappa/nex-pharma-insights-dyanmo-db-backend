"""
Simplified User Controller
Works with simplified UserService and UserModel
"""

from typing import List, Optional
from app.services.user_service import UserService
from app.core.response import ResponseFormatter, APIResponse
from app.core.logging import get_logger
from app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException, 
    InvalidCredentialsException
)

logger = get_logger("user_controller")

class UserController:
    """Simplified user controller with essential operations"""
    
    def __init__(self):
        self.user_service = UserService()
        self.logger = logger
    
    async def create_user(self, email: str, name: str, password: str, 
                         is_active: bool = True, role: str = 'user',
                         request_id: Optional[str] = None) -> APIResponse:
        """Create a new user"""
        try:
            user = await self.user_service.create_user(
                email=email,
                name=name,
                password=password,
                is_active=is_active,
                role=role
            )
            
            self.logger.info(f"User created successfully: {email}")
            return ResponseFormatter.created(
                data=user.to_response(),
                message=f"User {email} created successfully",
                request_id=request_id
            )
            
        except UserAlreadyExistsException as e:
            self.logger.error(f"User creation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "email", "message": "Email already exists"}],
                request_id=request_id
            )
            
        except Exception as e:
            self.logger.error(f"User creation failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to create user",
                errors=[{"error": str(e)}],
                request_id=request_id
            )
    
    async def get_user_by_id(self, user_id: str, request_id: Optional[str] = None) -> APIResponse:
        """Get user by ID"""
        try:
            user = await self.user_service.get_user_by_id(user_id)
            
            self.logger.info(f"User retrieved: {user_id}")
            return ResponseFormatter.success(
                data=user.to_response(),
                message="User retrieved successfully",
                request_id=request_id
            )
            
        except UserNotFoundException:
            self.logger.error(f"User not found: {user_id}")
            return ResponseFormatter.not_found(
                resource="User",
                request_id=request_id
            )
            
        except Exception as e:
            self.logger.error(f"Get user failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to retrieve user",
                errors=[{"error": str(e)}],
                request_id=request_id
            )
    
    async def get_user_by_email(self, email: str, request_id: Optional[str] = None) -> APIResponse:
        """Get user by email"""
        try:
            user = await self.user_service.get_user_by_email(email)
            
            self.logger.info(f"User retrieved by email: {email}")
            return ResponseFormatter.success(
                data=user.to_response(),
                message="User retrieved successfully",
                request_id=request_id
            )
            
        except UserNotFoundException:
            self.logger.error(f"User not found by email: {email}")
            return ResponseFormatter.not_found(
                resource="User",
                request_id=request_id
            )
            
        except Exception as e:
            self.logger.error(f"Get user by email failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to retrieve user",
                errors=[{"error": str(e)}],
                request_id=request_id
            )

    async def list_users(self, is_active: Optional[bool] = None, 
                        role: Optional[str] = None, 
                        limit: Optional[int] = None,
                        request_id: Optional[str] = None) -> APIResponse:
        """List users with filters"""
        try:
            users = await self.user_service.get_all_users(
                is_active=is_active,
                role=role,
                limit=limit
            )
            
            self.logger.info(f"Listed {len(users)} users")
            return ResponseFormatter.success(
                data=[user.to_response() for user in users],
                message=f"Retrieved {len(users)} users successfully",
                request_id=request_id
            )
            
        except Exception as e:
            self.logger.error(f"List users failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to retrieve users",
                errors=[{"error": str(e)}],
                request_id=request_id
            )
    