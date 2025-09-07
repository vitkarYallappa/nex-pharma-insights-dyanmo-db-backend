"""
Create Requests Table Migration
Created: 2024-12-01T12:04:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.requests_table import RequestsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_requests_table")

class CreateRequestsTableMigration(BaseMigration):
    """
    Create Requests Table Migration
    Creates the requests table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create requests table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating requests table migration")
        
        try:
            # Get requests table schema from configuration
            requests_schema = RequestsTableConfig.SCHEMA
            table_name = RequestsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the requests table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=requests_schema["key_schema"],
                attribute_definitions=requests_schema["attribute_definitions"],
                billing_mode=requests_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created requests table: {table_name}")
            else:
                logger.info(f"Requests table {table_name} already exists")
                
        except Exception as e:
            logger.error(f"Error creating requests table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back requests table creation")
        
        try:
            # Delete the requests table
            table_name = RequestsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted requests table: {table_name}")
            else:
                logger.warning(f"Requests table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting requests table: {str(e)}")
            raise 