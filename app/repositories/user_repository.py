"""
User Repository - Uses simplified base repository with only 4 methods
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.user_model import UserModel

class UserRepository(BaseRepository):
    """User repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(UserModel.table_name())
    
    async def create(self, user_model: UserModel) -> UserModel:
        """Create a new user"""
        user_data = user_model.to_dict()
        created_data = await super().create(user_data)
        return UserModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[UserModel]:
        """Find user by query"""
        user_data = await super().find_one_by_query(query)
        return UserModel.from_dict(user_data) if user_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[UserModel]:
        """Get all users with optional filters"""
        users_data = await super().find_all_by_query(query, limit)
        return [UserModel.from_dict(user_data) for user_data in users_data]
    
    async def update_by_query(self, query: Dict[str, Any], update_data: Dict[str, Any]) -> Optional[UserModel]:
        """Update user by query"""
        updated_data = await super().update_by_query(query, update_data)
        return UserModel.from_dict(updated_data) if updated_data else None
    
    # Convenience methods using the base methods
    async def find_user_by_id(self, user_id: str) -> Optional[UserModel]:
        """Find user by ID"""
        return await self.find_one_by_query({"user_id": user_id})
    
    async def find_user_by_email(self, email: str) -> Optional[UserModel]:
        """Find user by email"""
        return await self.find_one_by_query({"email": email})
    
    async def get_all_users(self, is_active: Optional[bool] = None, 
                           role: Optional[str] = None, 
                           limit: Optional[int] = None) -> List[UserModel]:
        """Get all users with optional filters"""
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        if role:
            query["role"] = role
            
        return await self.find_all_by_query(query, limit)
    