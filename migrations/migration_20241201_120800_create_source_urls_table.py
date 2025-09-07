"""
Create Source URLs Table Migration
Created: 2024-12-01T12:08:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.source_urls_table import SourceUrlsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_source_urls_table")

class CreateSourceUrlsTableMigration(BaseMigration):
    """
    Create Source URLs Table Migration
    Creates the source_urls table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create source_urls table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating source_urls table migration")
        
        try:
            # Get source URLs table schema from configuration
            urls_schema = SourceUrlsTableConfig.SCHEMA
            table_name = SourceUrlsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the source_urls table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=urls_schema["key_schema"],
                attribute_definitions=urls_schema["attribute_definitions"],
                billing_mode=urls_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created source_urls table: {table_name}")
            else:
                logger.info(f"Source_urls table {table_name} already exists")
                
        except Exception as e:
            logger.error(f"Error creating source_urls table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back source_urls table creation")
        
        try:
            # Delete the source_urls table
            table_name = SourceUrlsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted source_urls table: {table_name}")
            else:
                logger.warning(f"Source_urls table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting source_urls table: {str(e)}")
            raise 