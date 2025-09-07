"""
Create Global Keywords Table Migration
Created: 2024-12-01T12:05:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.global_keywords_table import GlobalKeywordsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_global_keywords_table")

class CreateGlobalKeywordsTableMigration(BaseMigration):
    """
    Create Global Keywords Table Migration
    Creates the global_keywords table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create global_keywords table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating global_keywords table migration")
        
        try:
            # Get global keywords table schema from configuration
            keywords_schema = GlobalKeywordsTableConfig.SCHEMA
            table_name = GlobalKeywordsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the global_keywords table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=keywords_schema["key_schema"],
                attribute_definitions=keywords_schema["attribute_definitions"],
                billing_mode=keywords_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created global_keywords table: {table_name}")
            else:
                logger.info(f"Global_keywords table {table_name} already exists")
                
        except Exception as e:
            logger.error(f"Error creating global_keywords table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back global_keywords table creation")
        
        try:
            # Delete the global_keywords table
            table_name = GlobalKeywordsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted global_keywords table: {table_name}")
            else:
                logger.warning(f"Global_keywords table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting global_keywords table: {str(e)}")
            raise 