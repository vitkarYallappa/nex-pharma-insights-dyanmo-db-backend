"""
Create Content URL Mapping Table Migration
Created: 2024-12-01T12:11:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.content_url_mapping_table import ContentUrlMappingTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_content_url_mapping_table")

class CreateContentUrlMappingTableMigration(BaseMigration):
    """
    Create Content URL Mapping Table Migration
    Creates the content_url_mapping table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create content_url_mapping table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating content_url_mapping table migration")
        
        try:
            # Get content URL mapping table schema from configuration
            mapping_schema = ContentUrlMappingTableConfig.SCHEMA
            table_name = ContentUrlMappingTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the content_url_mapping table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=mapping_schema["key_schema"],
                attribute_definitions=mapping_schema["attribute_definitions"],
                billing_mode=mapping_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created content_url_mapping table: {table_name}")
            else:
                logger.info(f"Content_url_mapping table {table_name} already exists")
                
        
            # Add some initial data if needed
            # await self._create_initial_data()
                
        except Exception as e:
            logger.error(f"Error creating content_url_mapping table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back content_url_mapping table creation")
        
        try:
            # Delete the content_url_mapping table
            table_name = ContentUrlMappingTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted content_url_mapping table: {table_name}")
            else:
                logger.warning(f"Content_url_mapping table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting content_url_mapping table: {str(e)}")
            raise
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data")
        
        try:
            # Placeholder for content-related tables
            # Actual implementation would depend on the specific table structure
            logger.info("Initial data creation placeholder - table ready for use")
                
        except Exception as e:
            logger.warning(f"Could not create initial data: {str(e)}") 