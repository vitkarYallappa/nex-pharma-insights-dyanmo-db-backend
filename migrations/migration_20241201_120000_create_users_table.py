"""
Create Users Table Migration
Created: 2024-12-01T12:00:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.users_table import UsersTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_users_table")

class CreateUsersTableMigration(BaseMigration):
    """
    Create Users Table Migration
    Creates the main users table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create users table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating users table migration")
        
        try:
            # Get users table schema from configuration
            users_schema = UsersTableConfig.SCHEMA
            table_name = UsersTableConfig.get_table_name()
            
            # Create the users table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=users_schema["key_schema"],
                attribute_definitions=users_schema["attribute_definitions"],
                billing_mode=users_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created users table: {table_name}")
            else:
                logger.info(f"Users table {table_name} already exists")
                
            # Add some initial data if needed
            await self._create_initial_data()
            
        except Exception as e:
            logger.error(f"Error creating users table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back users table creation")
        
        try:
            # Delete the users table
            table_name = UsersTableConfig.get_table_name()
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted users table: {table_name}")
            else:
                logger.warning(f"Users table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting users table: {str(e)}")
            raise
    
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data")
        
        try:
            from app.repositories.user_repository import UserRepository
            from app.models.user_model import UserModel
            from passlib.context import CryptContext
            
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            user_repo = UserRepository()
            
            # Check if admin user already exists
            admin_exists = await user_repo.exists({"email": "admin@example.com"})
            
            if not admin_exists:
                admin_user = UserModel.create_new(
                    email="admin@example.com",
                    name="System Administrator",
                    hashed_password=pwd_context.hash("admin123"),
                    is_active=True,
                    role="admin"
                )
                
                await user_repo.create(admin_user)
                logger.info("Created admin user: admin@example.com (password: admin123)")
            
            # Create a test user
            test_exists = await user_repo.exists({"email": "test@example.com"})
            
            if not test_exists:
                test_user = UserModel.create_new(
                    email="test@example.com",
                    name="Test User",
                    hashed_password=pwd_context.hash("test123"),
                    is_active=True,
                    role="user"
                )
                
                await user_repo.create(test_user)
                logger.info("Created test user: test@example.com (password: test123)")
                
        except Exception as e:
            logger.warning(f"Could not create initial data (this is normal if running for the first time): {str(e)}")