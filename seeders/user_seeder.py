"""
User Seeder
Populates initial user data for development and testing
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from seeders.base_seeder import BaseSeeder
from app.repositories.user_repository import UserRepository
from app.models.user_model import UserModel
from passlib.context import CryptContext
from typing import List, Dict, Any

class UserSeeder(BaseSeeder):
    """Seeder for initial user data"""
    
    def __init__(self):
        super().__init__()
        self.user_repo = UserRepository()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
    @property
    def name(self) -> str:
        return "UserSeeder"
    
    @property
    def description(self) -> str:
        return "Seeds initial user accounts (admin, test users)"
    
    async def seed(self) -> bool:
        """Populate initial user data"""
        try:
            self.log_info("Starting user seeding...")
            
            users_data = self._get_seed_data()
            created_count = 0
            
            for user_data in users_data:
                # Check if user already exists
                existing_user = await self.user_repo.find_user_by_email(user_data["email"])
                
                if existing_user:
                    self.log_info(f"User {user_data['email']} already exists, skipping...")
                    continue
                
                # Create new user
                user = UserModel.create_new(
                    email=user_data["email"],
                    name=user_data["name"],
                    hashed_password=self.pwd_context.hash(user_data["password"]),
                    is_active=user_data.get("is_active", True),
                    role=user_data.get("role", "user")
                )
                
                await self.user_repo.create(user)
                created_count += 1
                
                self.log_info(f"Created user: {user_data['email']} (role: {user_data.get('role', 'user')})")
            
            self.log_info(f"User seeding completed. Created {created_count} users")
            return True
            
        except Exception as e:
            self.log_error(f"User seeding failed: {str(e)}")
            return False
    
    async def clear(self) -> bool:
        """Clear seeded user data"""
        try:
            self.log_info("Starting user data cleanup...")
            
            users_data = self._get_seed_data()
            deleted_count = 0
            
            for user_data in users_data:
                # Find and delete user
                existing_user = await self.user_repo.find_user_by_email(user_data["email"])
                
                if existing_user:
                    # Delete user by updating query (since we don't have a direct delete method)
                    # This is a simplified approach - in production you might want a proper delete method
                    await self.user_repo.update_by_query(
                        {"user_id": existing_user.user_id},
                        {"is_active": False, "email": f"deleted_{existing_user.email}"}
                    )
                    deleted_count += 1
                    self.log_info(f"Deactivated user: {user_data['email']}")
                else:
                    self.log_info(f"User {user_data['email']} not found, skipping...")
            
            self.log_info(f"User cleanup completed. Deactivated {deleted_count} users")
            return True
            
        except Exception as e:
            self.log_error(f"User cleanup failed: {str(e)}")
            return False
    
    def _get_seed_data(self) -> List[Dict[str, Any]]:
        """Get the seed data for users"""
        return [
            {
                "email": "admin@nexpharmacorp.com",
                "name": "System Administrator",
                "password": "admin123!",
                "role": "admin",
                "is_active": True
            },
            {
                "email": "manager@nexpharmacorp.com", 
                "name": "Pharmacy Manager",
                "password": "manager123!",
                "role": "manager",
                "is_active": True
            },
            {
                "email": "pharmacist@nexpharmacorp.com",
                "name": "Senior Pharmacist",
                "password": "pharma123!",
                "role": "pharmacist",
                "is_active": True
            },
            {
                "email": "analyst@nexpharmacorp.com",
                "name": "Data Analyst",
                "password": "analyst123!",
                "role": "analyst",
                "is_active": True
            },
            {
                "email": "test.user@nexpharmacorp.com",
                "name": "Test User",
                "password": "test123!",
                "role": "user",
                "is_active": True
            },
            {
                "email": "demo.user@nexpharmacorp.com",
                "name": "Demo User",
                "password": "demo123!",
                "role": "user",
                "is_active": True
            }
        ] 