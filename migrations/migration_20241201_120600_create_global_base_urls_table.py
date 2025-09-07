"""
Create Global Base URLs Table Migration
Created: 2024-12-01T12:06:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.global_base_urls_table import GlobalBaseUrlsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_global_base_urls_table")

class CreateGlobalBaseUrlsTableMigration(BaseMigration):
    """
    Create Global Base URLs Table Migration
    Creates the global_base_urls table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create global_base_urls table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating global_base_urls table migration")
        
        try:
            # Get global base URLs table schema from configuration
            urls_schema = GlobalBaseUrlsTableConfig.SCHEMA
            table_name = GlobalBaseUrlsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the global_base_urls table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=urls_schema["key_schema"],
                attribute_definitions=urls_schema["attribute_definitions"],
                billing_mode=urls_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created global_base_urls table: {table_name}")
            else:
                logger.info(f"Global_base_urls table {table_name} already exists")
                
        except Exception as e:
            logger.error(f"Error creating global_base_urls table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back global_base_urls table creation")
        
        try:
            # Delete the global_base_urls table
            table_name = GlobalBaseUrlsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted global_base_urls table: {table_name}")
            else:
                logger.warning(f"Global_base_urls table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting global_base_urls table: {str(e)}")
            raise 